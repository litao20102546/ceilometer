# Copyright 2014 Intel
#
# Author: Zhai Edwin <edwin.zhai@intel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import abc
import mock
import six

from ceilometer.ipmi import manager
import ceilometer.tests.base as base

from oslotest import mockpatch


@six.add_metaclass(abc.ABCMeta)
class TestPollsterBase(base.BaseTestCase):

    @abc.abstractmethod
    def fake_data(self):
        """Fake data used for test."""

    @abc.abstractmethod
    def fake_sensor_data(self, sensor_type):
        """Fake sensor data used for test."""

    @abc.abstractmethod
    def make_pollster(self):
        """Produce right pollster for test."""

    def _test_get_samples(self):
        nm = mock.Mock()
        nm.read_temperature_all.side_effect = self.fake_data
        nm.read_power_all.side_effect = self.fake_data
        nm.read_sensor_any.side_effect = self.fake_sensor_data
        # We should mock the pollster first before initialize the Manager
        # so that we don't trigger the sudo in pollsters' __init__().
        self.useFixture(mockpatch.Patch(
            'ceilometer.ipmi.platform.intel_node_manager.NodeManager',
            return_value=nm))

        self.useFixture(mockpatch.Patch(
            'ceilometer.ipmi.platform.ipmi_sensor.IPMISensor',
            return_value=nm))

        self.mgr = manager.AgentManager()

        self.pollster = self.make_pollster()

    def _verify_metering(self, length, expected_vol=None, node=None):
        cache = {}
        resources = {}

        samples = list(self.pollster.get_samples(self.mgr, cache, resources))
        self.assertEqual(length, len(samples))

        if expected_vol:
            self.assertTrue(any(s.volume == expected_vol for s in samples))
        if node:
            self.assertTrue(any(s.resource_metadata['node'] == node
                                for s in samples))
