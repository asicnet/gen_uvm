

  int COV = 1;

  covergroup m_cov;
    option.per_instance = 1;
    // You may insert additional coverpoints here ...
    //  bins start = (0=>1);
    //  bins stop  = (1=>0);
    //  bins b1   = {1 };
    //  bins b2   = {[2:4]};

    cp_sl_send_data: coverpoint m_item.sl_send_data {
      bins all = {[0:$]};
    }

    cp_target: coverpoint m_item.target {
      bins all = {[0:$]};
    }


  endgroup

  covergroup TestCoverageGroup;
    option.per_instance = 1;

    cp_sl_get_data: coverpoint m_item.sl_get_data {
      bins all = {[0:$]};
    }

    cp_sl_sel: coverpoint m_item.sl_sel {
      bins all = {[0:$]};
    }

    cp_sl_enable: coverpoint m_item.sl_enable {
      bins all = {[0:$]};
    }

    cp_target: coverpoint m_item.target {
      bins all = {[0:$]};
    }

  endgroup

function new(string name, uvm_component parent);
  super.new(name, parent);
  m_is_covered = 0;
  m_cov = new();
  TestCoverageGroup = new();
endfunction : new


function void write(input slave_item t);
  if (m_config.coverage_enable) // && t.target == COV)
  begin
    m_item = t;
    m_cov.sample();
    TestCoverageGroup.sample();
    // Check coverage - could use m_cov.option.goal instead of 100 if your simulator supports it
    if ( TestCoverageGroup .get_inst_coverage() >= 100 
         &&  m_cov.get_inst_coverage() >= 100
       ) m_is_covered = 1;
  end
endfunction : write


function void build_phase(uvm_phase phase);
  if (!uvm_config_db #(slave_config)::get(this, "", "config", m_config))
    `uvm_error(get_type_name(), "slave config not found")
endfunction : build_phase


function void report_phase(uvm_phase phase);
  if (m_config.coverage_enable)
  begin
    `uvm_info(get_type_name(), $sformatf("Coverage score = %3.1f%%", m_cov.get_inst_coverage()), UVM_MEDIUM)
    `uvm_info(get_type_name(), $sformatf("TestCoverageGroup Coverage score = %3.1f%%", TestCoverageGroup.get_inst_coverage()), UVM_MEDIUM)
  end
  else
  begin
    `uvm_info(get_type_name(), "Coverage disabled for this agent", UVM_MEDIUM)
  end
endfunction : report_phase
