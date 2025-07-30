# Copyright 2023 Red Hat
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.common import waiters
from tempest import config

from whitebox_tempest_plugin.api.compute import base
from whitebox_tempest_plugin import hardware
from whitebox_tempest_plugin.services import clients


CONF = config.CONF


class TestCPUStateMgmt(base.BaseWhiteboxComputeTest):
    """Test Nova's CPU state management feature, ensuring that CPUs are
    onlined and offlined at the expected times.
    """
    min_microversion = '2.95'

    @classmethod
    def skip_checks(cls):
        super(TestCPUStateMgmt, cls).skip_checks()
        if not CONF.compute_feature_enabled.cpu_power_management:
            raise cls.skipException(
                'Libvirt CPU power is unavailable, skipping.')

    def setUp(self):
        super(TestCPUStateMgmt, self).setUp()
        self.flavor = self.create_flavor(
            vcpus=1,
            extra_specs={'hw:cpu_policy': 'dedicated'})

    def test_cpu_state(self):
        host = self.list_compute_hosts()[0]
        sysfsclient = clients.SysFSClient(host)
        sm = clients.NovaServiceManager(host, 'nova-compute',
                                        self.os_admin.services_client)
        dedicated_cpus = sm.get_cpu_dedicated_set()
        shared_cpus = sm.get_cpu_shared_set()
        # Nova offlines all unused cpu's from the dedicated set
        # except for cpu0 because it is not hot pluggable
        # Hence modifying to exclude it avoid false test failures.
        dedicated_cpus.discard(0)

        if len(dedicated_cpus) < 2:
            raise self.skipException('Multiple dedicated CPUs required')

        # Assert that nova-compute disabled dedicated CPUs on startup. In case
        # we didn't have a full set specified, at least make sure that our
        # shared CPUs are in the subset of online CPUs (i.e. we didn't offline
        # any of the shared ones).
        online = sysfsclient.get_sysfs_value('devices/system/cpu/online')
        self.assertTrue(shared_cpus.issubset(hardware.parse_cpu_spec(online)))

        # All our dedicated CPUs should be offlined (this assumes running
        # serially with no other guests using the dedicated CPUs).
        offline_before = hardware.parse_cpu_spec(
            sysfsclient.get_sysfs_value('devices/system/cpu/offline'))
        self.assertEqual(dedicated_cpus, offline_before)

        server = self.create_test_server(clients=self.os_admin,
                                         flavor=self.flavor['id'],
                                         host=host,
                                         wait_until='ACTIVE')

        # Our test server should have caused nova to online our dedicated CPU
        offline_after = hardware.parse_cpu_spec(
            sysfsclient.get_sysfs_value('devices/system/cpu/offline'))
        self.assertLess(offline_after, offline_before)

        self.os_admin.servers_client.delete_server(server['id'])
        waiters.wait_for_server_termination(self.os_admin.servers_client,
                                            server['id'])

        # Once it is gone, the dedicated CPU should be offline again
        offline_final = hardware.parse_cpu_spec(
            sysfsclient.get_sysfs_value('devices/system/cpu/offline'))
        self.assertEqual(offline_before, offline_final)
