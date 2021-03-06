import wishful_upis as upis
import wishful_framework as wishful_module
from wishful_framework.classes import exceptions
from wishful_framework.upi_arg_classes.net_classes import NetworkInfo #<----!!!!! Important to include it here; otherwise cannot be pickled!!!!
from wishful_module_gitar.lib_gitar import SensorNode
from wishful_module_gitar.lib_gitar import SensorNodeFactory

import logging
import inspect

@wishful_module.build_module
class RIMEConnector(wishful_module.AgentModule):
	def __init__(self,**kwargs):
		super(RIMEConnector, self).__init__()
		self.log = logging.getLogger('RIMEConnector')
		self.node_factory = SensorNodeFactory()
		#~ self.supported_interfaces = kwargs['SupportedInterfaces']
		#~ rime_control_extensions = kwargs['ControlExtensions']
		#~ self.params = []
		#~ self.measurements = []
		#~ self.events = []
		#~ try:
			#~ file_rp = open(rime_control_extensions,'rt')
			#~ reader = csv.DictReader(file_rp)
			#~ param_defs = []
			#~ measurement_defs = []
			#~ event_defs = []
			#~ for row in reader:
				#~ r_def = {'unique_name' : row["unique_name"], 'unique_id' : row["unique_id"], 'type_name' : row["type"], 'type_len' : row["length"], 'type_format' : row["struct_format"]}
				#~ if row['category'] == "PARAMETER":
					#~ self.params.append(row["unique_name"])
					#~ param_defs.append(r_def)
				#~ elif row['category'] == "MEASUREMENT":
					#~ self.measurements.append(row["unique_name"])
					#~ measurement_defs.append(r_def)
				#~ elif row['category'] == "EVENT":
					#~ self.events.append(row["unique_name"])
					#~ event_defs.append(r_def)
				#~ else:
					#~ self.log.info("Illegal parameter category: %s" % row['category'])
			#~ 
			#~ for iface in self.supported_interfaces:
				#~ node = self.node_factory.get_node(iface)
				#~ node.register_parameters(param_defs)
				#~ node.register_measurements(measurement_defs)
				#~ node.register_events(event_defs)
			
		#~ except Exception as e:
			#~ self.log.fatal("An error occurred while initializing TAISC: %s" % e)
		
	@wishful_module.bind_function(upis.net.get_iface_ip_addr)
	def get_ipaddr(self):
		return self.node.ip_addr
	
	@wishful_module.bind_function(upis.net.get_parameters)
	def get_network_parameters(self, param_keys):
		node = self.node_factory.get_node(self.interface)
		if node != None:
			return node.read_parameters('rime', param_keys)
		else:
			fname = inspect.currentframe().f_code.co_name
			self.log.fatal("%s Interface %s does not exist!" % (self.interface, fname))
			raise exceptions.InvalidArgumentException(func_name=fname, err_msg="Interface does not exist")
	
	@wishful_module.bind_function(upis.net.set_parameters)
	def set_network_parameters(self, param_key_values):
		node = self.node_factory.get_node(self.interface)
		if node != None:
			return node.write_parameters('rime', param_key_values)
		else:
			fname = inspect.currentframe().f_code.co_name
			self.log.fatal("%s Interface %s does not exist!" % (self.interface, fname))
			raise exceptions.InvalidArgumentException(func_name=fname, err_msg="Interface does not exist")
	
	@wishful_module.bind_function(upis.net.get_measurements)
	def get_network_measurements(self, measurement_keys):
		node = self.node_factory.get_node(self.interface)
		if node != None:
			return node.get_measurements('rime', measurement_keys)
		else:
			fname = inspect.currentframe().f_code.co_name
			self.log.fatal("%s Interface %s does not exist!" % (self.interface, fname))
			raise exceptions.InvalidArgumentException(func_name=fname, err_msg="Interface does not exist")

	def get_network_measurements_periodic_worker(self, node, measurement_keys, collect_period, report_period, num_iterations,report_callback):
		num_collects_report = report_period / collect_period
		for i in xrange(0,num_iterations):
			measurement_report = {}
			for key in measurement_keys:
				measurement_report[key] = []
			for i in xrange(0,num_collects_report):
				time.sleep(collect_period)
				ret = node.get_measurements('rime', measurement_keys)
				for key in ret.keys():
					measurement_report[key].append(ret[key])
			report_callback(node.interface, measurement_report)
		pass

	@wishful_module.bind_function(upis.net.get_measurements_periodic)
	def get_network_measurements_periodic(self, measurement_keys, collect_period, report_period, num_iterations,report_callback):
		node = self.node_factory.get_node(self.interface)
		if node != None:
			thread.start_new_thread(self.get_network_measurements_periodic_worker, (node,measurement_keys, collect_period, report_period, num_iterations,report_callback,))
		else:
			fname = inspect.currentframe().f_code.co_name
			self.log.fatal("%s Interface %s does not exist!" % (self.interface, fname))
			raise exceptions.InvalidArgumentException(func_name=fname, err_msg="Interface does not exist")

	@wishful_module.bind_function(upis.net.define_events)
	def define_network_event(self, event_keys, event_callback):
		node = self.node_factory.get_node(self.interface)
		if node != None:
			return node.define_events('rime',event_keys,event_callback)
		else:
			fname = inspect.currentframe().f_code.co_name
			self.log.fatal("%s Interface %s does not exist!" % (self.interface, fname))
			raise exceptions.InvalidArgumentException(func_name=fname, err_msg="Interface does not exist")
	
	@wishful_module.bind_function(upis.net.get_info)
	def get_network_info(self):
		node = self.node_factory.get_node(self.interface)
		if node != None:
			return NetworkInfo(self.node.ip_addr, node.params_name_dct['rime'].keys(), node.measurements_name_dct['rime'].keys(), node.events_name_dct['rime'].keys())
		else:
			fname = inspect.currentframe().f_code.co_name
			self.log.fatal("%s Interface %s does not exist!" % (self.interface, fname))
			raise exceptions.InvalidArgumentException(func_name=fname, err_msg="Interface does not exist")
