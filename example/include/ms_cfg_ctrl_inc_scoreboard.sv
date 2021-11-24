int write_clock_reset_cnt   = 0;
//clock_reset_item item;
int write_master_cnt   = 0;
//master_item item;
int write_register_cnt   = 0;
//register_item item;
int write_slave_cnt   = 0;
//slave_item item;
int write_target_cnt   = 0;
//target_item item;

function new(string name, uvm_component parent);
  super.new(name, parent);
endfunction : new

function void write_clock_reset(input clock_reset_item t);
  begin
    clock_reset_item item = t;
    $cast(item,t.clone());
    //$display("clock_reset",item.sprint());
    write_clock_reset_cnt++;
  end
endfunction

function void write_master(input master_item t);
  begin
    master_item item = t;
    $cast(item,t.clone());
    //$display("master",item.sprint());
    write_master_cnt++;
  end
endfunction

function void write_register(input register_item t);
  begin
    register_item item = t;
    $cast(item,t.clone());
    //$display("register",item.sprint());
    write_register_cnt++;
  end
endfunction

function void write_slave(input slave_item t);
  begin
    slave_item item = t;
    $cast(item,t.clone());
    //$display("slave",item.sprint());
    write_slave_cnt++;
  end
endfunction

function void write_target(input target_item t);
  begin
    target_item item = t;
    $cast(item,t.clone());
    //$display("target",item.sprint());
    write_target_cnt++;
  end
endfunction
function void build_phase(uvm_phase phase);

  if (!uvm_config_db #(clock_reset_config)::get(this, "", "config", m_clock_reset_config))
    `uvm_error(get_type_name(), "clock_reset config not found")

  if (!uvm_config_db #(master_config)::get(this, "", "config", m_master_config))
    `uvm_error(get_type_name(), "master config not found")

  if (!uvm_config_db #(register_config)::get(this, "", "config", m_register_config))
    `uvm_error(get_type_name(), "register config not found")

  if (!uvm_config_db #(slave_config)::get(this, "", "config", m_slave_config))
    `uvm_error(get_type_name(), "slave config not found")

  if (!uvm_config_db #(target_config)::get(this, "", "config", m_target_config))
    `uvm_error(get_type_name(), "target config not found")

endfunction

function void report_phase(uvm_phase phase);
  `uvm_info(get_type_name(), "Scoreboard is enabled for this agent_instance", UVM_MEDIUM)
  `uvm_info(get_type_name(), $sformatf({"Result of Transaction counters !\n\n"
                                        ,"\n  write_clock_reset_cnt = %0d "
                                        ,"\n  write_master_cnt = %0d "
                                        ,"\n  write_register_cnt = %0d "
                                        ,"\n  write_slave_cnt = %0d "
                                        ,"\n  write_target_cnt = %0d "
                                        ,"\n\n"}
                                         , write_clock_reset_cnt, write_master_cnt, write_register_cnt, write_slave_cnt, write_target_cnt
                                        ), UVM_MEDIUM)
endfunction

