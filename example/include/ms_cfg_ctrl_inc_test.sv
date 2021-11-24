  // Start the active sequencer

  clock_reset_test_seq m_clock_reset;
  master_test_seq      m_master;
  register_test_seq    m_register;
  slave_test_seq       m_slave;

  //------------------------------------------

  int        max = 1000;
  top_config m_config;

  //==========================================
  // common.tpl
  // nested_config_objects              = yes
  // config_var = int top_test_start_nr = 1;
  // config_var = int top_test_end_nr   = 1;

  function bit check_test_nr(int test_nr);

    if (!uvm_config_db #(top_config)::get(this, "", "config", m_config))
      `uvm_error(get_type_name(), "Unable to get top_config")

    if ( m_config.top_test_start_nr <= test_nr &&  m_config.top_test_end_nr >= test_nr) return 1;
    else return 0;

  endfunction  // check_test_nr

  task reset_phase (uvm_phase phase);
    super.reset_phase(phase);
    
    phase.raise_objection(this);
      `uvm_info(get_type_name(), "Wait the posedge of the rst_n", UVM_LOW)
      #75ns;
      `uvm_info(get_type_name(), "Detected posedge of the rst_n", UVM_LOW)
    phase.drop_objection(this);
    
  endtask // reset_phase

  task main_phase (uvm_phase phase);

    if (!uvm_config_db #(top_config)::get(this, "", "config", m_config))
      `uvm_error(get_type_name(), "Unable to get top_config")
    `uvm_info(get_type_name(), "start main_phase()", UVM_LOW)    
    m_clock_reset  = clock_reset_test_seq  ::type_id::create("m_clock_reset");
    m_master       = master_test_seq       ::type_id::create("m_master");
    m_register     = register_test_seq     ::type_id::create("m_register");
    m_slave        = slave_test_seq        ::type_id::create("m_slave");

    phase.raise_objection(this);

    begin

      int found = 0;
      string  clock_reset_test_name []  = '{
                                               "RESET_VALUES"  // 1
                                              ,"SET_SIGNALS"   // 2
                                           };

      string  master_test_name []       = '{
                                               "RESET_VALUES"  // 1
                                              ,"SET_SIGNALS"   // 2
                                           };

      string  register_test_name []     = '{
                                               "RESET_VALUES"  // 1
                                              ,"SET_SIGNALS"   // 2
                                           };

      string  slave_test_name []        = '{
                                               "RESET_VALUES"  // 1
                                              ,"SET_SIGNALS"   // 2
                                           };

      max = clock_reset_test_name.size  < max ? clock_reset_test_name.size  : max;
//    max = clock_reset_test_name.size  < max ? clock_reset_test_name.size  : max;
//    max = master_test_name.size       < max ? master_test_name.size       : max;
//    max = register_test_name.size     < max ? register_test_name.size     : max;
//    max = slave_test_name.size        < max ? slave_test_name.size        : max;


      for (int i = 1; i <= max ; i++) begin
        m_config  .m_clock_reset_config  .checks_enable  = 1;
        m_config  .m_master_config       .checks_enable  = 1;
        m_config  .m_register_config     .checks_enable  = 1;
        m_config  .m_slave_config        .checks_enable  = 1;


        // Disable checks in monitor
        // if ( i == 1 ) begin
//          m_config  .m_clock_reset_config  .checks_enable  = 0;
//          m_config  .m_master_config       .checks_enable  = 0;
//          m_config  .m_register_config     .checks_enable  = 0;
//          m_config  .m_slave_config        .checks_enable  = 0;

        //end

        if ( check_test_nr(i) ) begin
          found++;
          if (m_config.m_clock_reset_config.is_active) m_clock_reset  .test_name = clock_reset_test_name [i-1];
          if (m_config.m_master_config.is_active) m_master            .test_name = master_test_name      [i-1];
          if (m_config.m_register_config.is_active) m_register        .test_name = register_test_name    [i-1];
          if (m_config.m_slave_config.is_active) m_slave              .test_name = slave_test_name       [i-1];


          fork
            if (m_config.m_clock_reset_config.is_active) m_clock_reset  .start( m_env .m_clock_reset_agent  .m_sequencer );
            if (m_config.m_master_config.is_active) m_master            .start( m_env .m_master_agent       .m_sequencer );
            if (m_config.m_register_config.is_active) m_register        .start( m_env .m_register_agent     .m_sequencer );
            if (m_config.m_slave_config.is_active) m_slave              .start( m_env .m_slave_agent        .m_sequencer );

          join
        end
      end

      assert(found>0) else begin
        `uvm_fatal(get_type_name(), "No test number in Range!")
        $fatal("No test number in Range!");
      end
    end
    phase.drop_objection(this);
   endtask

  function void build_phase(uvm_phase phase);
    super.build_phase (phase);
    m_env = top_env::type_id::create("m_env", this);
  endfunction : build_phase

