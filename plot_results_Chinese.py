# -*- coding:UTF-8 -*-
# Copyright (C) 2016 Huang MaChi at Chongqing University
# of Posts and Telecommunications, Chongqing, China.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
chinese_font = FontProperties(fname='/usr/share/matplotlib/mpl-data/fonts/ttf/simhei.ttf')
import numpy as np


def read_file_1(file_name, delim=','):
	"""
		Read the bwmng.txt file.
	"""
	read_file = open(file_name, 'r')
	lines = read_file.xreadlines()
	lines_list = []
	for line in lines:
		line_list = line.strip().split(delim)
		lines_list.append(line_list)
	read_file.close()

	# Remove the last second's statistics, because they are mostly not intact.
	last_second = lines_list[-1][0]
	_lines_list = lines_list[:]
	for line in _lines_list:
		if line[0] == last_second:
			lines_list.remove(line)

	return lines_list

def read_file_2(file_name):
	"""
		Read the ping.txt file.
	"""
	read_file = open(file_name, 'r')
	lines = read_file.xreadlines()
	lines_list = []
	for line in lines:
		if line.endswith(' ms\n') and not line.startswith('rtt'):
			lines_list.append(line)
	read_file.close()
	return lines_list

def get_total_throughput(total_throughput):
	"""
		total_throughput = {0:x, 1:x, 2:x, ...}
	"""
	lines_list = read_file_1('./results/bwmng.txt')
	first_second = int(lines_list[0][0])
	column_bytes_out = 6   # bytes_out
	switch = 's2'
	sw = re.compile(switch)
	realtime_throught = {}

	for i in xrange(121):
		if not total_throughput.has_key(i):
			total_throughput[i] = 0

	for i in xrange(121):
		if not realtime_throught.has_key(i):
			realtime_throught[i] = 0

	for row in lines_list:
		iface_name = row[1]
		if sw.match(iface_name):
			if int(iface_name[-1]) <= 3:   # Choose host-connecting interfaces only.
				if (int(row[0]) - first_second) <= 120:   # Take the good values only.
					realtime_throught[int(row[0]) - first_second] += float(row[column_bytes_out]) * 8.0 / (10 ** 6)   # Mbit

	for i in xrange(121):
		for j in xrange(i+1):
			total_throughput[i] += realtime_throught[j]   # Mbit

	return total_throughput

def get_value_list_1(value_dict):
	"""
		Get the values from the "total_throughput" data structure.
	"""
	value_list = []
	for i in xrange(121):
		value_list.append(value_dict[i])
	return value_list

def get_value_list_2(value_dict):
	"""
		Get the values from the "roundtrip_delay" data structure.
	"""
	value_list = [0]
	sequence_list = [0]
	for i in xrange(121):
		if value_dict[i] != 0:
			sequence_list.append(i)
			value_list.append(value_dict[i])
	return sequence_list, value_list

def get_value_list_3(value_dict, sequence):
	"""
		Get the values from the "roundtrip_delay" data structure.
	"""
	num = 0
	for i in xrange(sequence, sequence + 30):
		if i != 0:
			if value_dict[i] == 0:
				num += 1
	rate = num / 30.0
	return rate

def get_value_list_4(value_dict):
	"""
		Get the values from the "roundtrip_delay" data structure.
	"""
	value_list = [0]
	sequence_list = [0]
	for i in xrange(61):
		if value_dict[i] != 0:
			sequence_list.append(i)
			value_list.append(value_dict[i])
	return sequence_list, value_list

def get_realtime_speed(switch):
	"""
		Get realtime speed of individual flow.
	"""
	realtime_speed = {}
	lines_list = read_file_1('./results/bwmng.txt')
	first_second = int(lines_list[0][0])
	column_bytes_out_rate = 2   # bytes_out/s
	sw = re.compile(switch)

	for i in xrange(121):
		if not realtime_speed.has_key(i):
			realtime_speed[i] = 0

	for row in lines_list:
		iface_name = row[1]
		if sw.match(iface_name):
			if (int(row[0]) - first_second) <= 120:   # Take the good values only.
				realtime_speed[int(row[0]) - first_second] += float(row[column_bytes_out_rate]) * 8.0 / (10 ** 6)   # Mbit/s

	return realtime_speed

def get_delay_values(delay_dict):
	"""
		Get round trip delay of ping traffic.
	"""
	lines_list = read_file_2('./results/ping.txt')
	for i in xrange(121):
		if not delay_dict.has_key(i):
			delay_dict[i] = 0

	for row in lines_list:
		sequence = int(row.split(' ')[4].split('=')[1])
		delay = float(row.split(' ')[6].split('=')[1])
		delay_dict[sequence] = delay

	return delay_dict

def plot_results():
	"""
		Plot the results:
		1. Plot total throughput
		2. Plot realtime speed of individual flow
	"""
	bandwidth = 10.0   # (unit: Mbit/s)
	utmost_throughput = bandwidth * 120
	total_throughput = {}
	total_throughput = get_total_throughput(total_throughput)
	roundtrip_delay = {}
	roundtrip_delay = get_delay_values(roundtrip_delay)

	# 1. Plot total throughput.
	fig = plt.figure()
	fig.set_size_inches(12, 6)
	x = np.arange(0, 121)
	y = get_value_list_1(total_throughput)
	plt.plot(x, y, 'r-', linewidth=2)
	plt.xlabel(u'时间 (s)', fontsize='xx-large', fontproperties=chinese_font)
	plt.xlim(0, 120)
	plt.xticks(np.arange(0, 121, 30))
	plt.ylabel(u'网络总吞吐量\n(Mbit)', fontsize='xx-large', fontproperties=chinese_font)
	plt.ylim(0, utmost_throughput)
	plt.yticks(np.linspace(0, utmost_throughput, 11))
	plt.grid(True)
	plt.savefig('./results/1.network_total_throughput.png')

	# 2. Plot realtime speed of individual flow.
	fig = plt.figure()
	fig.set_size_inches(12, 6)
	x = np.arange(0, 121)
	realtime_speed1 = get_realtime_speed('s2-eth1')
	y1 = get_value_list_1(realtime_speed1)
	realtime_speed2 = get_realtime_speed('s2-eth2')
	y2 = get_value_list_1(realtime_speed2)
	realtime_speed3 = get_realtime_speed('s2-eth3')
	y3 = get_value_list_1(realtime_speed3)
	plt.plot(x, y1, 'r-', linewidth=2, label="Ping")
	plt.plot(x, y2, 'g-', linewidth=2, label="Iperf1")
	plt.plot(x, y3, 'b-', linewidth=2, label="Iperf2")
	plt.xlabel(u'时间 (s)', fontsize='xx-large', fontproperties=chinese_font)
	plt.xlim(0, 120)
	plt.xticks(np.arange(0, 121, 30))
	plt.ylabel(u'每条流的实时速率\n(Mbit/s)', fontsize='xx-large', fontproperties=chinese_font)
	plt.ylim(0, bandwidth)
	plt.yticks(np.linspace(0, bandwidth, 11))
	plt.legend(loc='upper right', ncol=3, fontsize='small')
	plt.grid(True)
	plt.savefig('./results/2.realtime_speed_of_individual_flow.png')

	# 3. Plot realtime throughput.
	fig = plt.figure()
	fig.set_size_inches(12, 6)
	x = np.arange(0, 121)
	realtime_speed = get_realtime_speed('s2-eth[1-3]')
	y = get_value_list_1(realtime_speed)
	plt.plot(x, y, 'r-', linewidth=2)
	plt.xlabel(u'时间 (s)', fontsize='xx-large', fontproperties=chinese_font)
	plt.xlim(0, 120)
	plt.xticks(np.arange(0, 121, 30))
	plt.ylabel(u'网络单位时间吞吐量\n(Mbit/s)', fontsize='xx-large', fontproperties=chinese_font)
	plt.ylim(0, bandwidth)
	plt.yticks(np.linspace(0, bandwidth, 11))
	plt.grid(True)
	plt.savefig('./results/3.network_unit_time_throught.png')

	# 4. Plot round-trip delay of ping traffic.
	fig = plt.figure()
	fig.set_size_inches(12, 6)
	x, y = get_value_list_2(roundtrip_delay)
	plt.plot(x, y, 'r-', linewidth=2)
	plt.xlabel(u'时间 (s)', fontsize='xx-large', fontproperties=chinese_font)
	plt.xlim(0, 120)
	plt.xticks(np.arange(0, 121, 30))
	plt.ylabel(u'Ping流量的往返时延\n(ms)', fontsize='xx-large', fontproperties=chinese_font)
	# plt.ylim(0, bandwidth)
	# plt.yticks(np.linspace(0, bandwidth, 11))
	plt.grid(True)
	plt.savefig('./results/4.round-trip_delay_of_ping_traffic.png')

	# 4-2. Plot round-trip delay of ping traffic.
	fig = plt.figure()
	fig.set_size_inches(12, 6)
	x, y = get_value_list_4(roundtrip_delay)
	plt.plot(x, y, 'r-', linewidth=2)
	plt.xlabel(u'时间 (s)', fontsize='xx-large', fontproperties=chinese_font)
	plt.xlim(0, 60)
	plt.xticks(np.arange(0, 61, 30))
	plt.ylabel(u'Ping流量的往返时延\n(ms)', fontsize='xx-large', fontproperties=chinese_font)
	# plt.yticks(np.linspace(0, 50, 6))
	plt.grid(True)
	plt.savefig('./results/4-2.round-trip_delay_of_ping_traffic.png')

	# 5. Plot packet loss rate of ping traffic.
	fig = plt.figure()
	fig.set_size_inches(12, 6)
	num_groups = 1
	num_bar = 4
	first_thirty = get_value_list_3(roundtrip_delay, 0)
	second_thirty = get_value_list_3(roundtrip_delay, 30)
	third_thirty = get_value_list_3(roundtrip_delay, 60)
	fourth_thirty = get_value_list_3(roundtrip_delay, 90)
	index = np.arange(num_groups)
	bar_width = 30
	plt.bar(index, first_thirty, bar_width, color='r', label='0-30s')
	plt.bar(index + 1 * bar_width, second_thirty, bar_width, color='g', label='30-60s')
	plt.bar(index + 2 * bar_width, third_thirty, bar_width, color='b', label='60-90s')
	plt.bar(index + 3 * bar_width, fourth_thirty, bar_width, color='y', label='90-120s')
	plt.xlabel(u'时间 (s)', fontsize='xx-large', fontproperties=chinese_font)
	plt.xlim(0, 120)
	plt.xticks(np.linspace(0, 120, 5))
	plt.ylabel(u'Ping流量的丢包率\n', fontsize='xx-large', fontproperties=chinese_font)
	plt.ylim(0, 1)
	plt.yticks(np.linspace(0, 1, 11))
	plt.legend(loc='upper right', fontsize='medium')
	plt.grid(axis='y')
	plt.savefig('./results/5.packet_loss_rate_of_ping_traffic.png')


if __name__ == '__main__':
	plot_results()
