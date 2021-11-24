

  task run_phase(uvm_phase phase);
    `uvm_info(get_type_name(), "run_phase", UVM_HIGH)
    forever
    begin
      seq_item_port.get_next_item(req);
      `uvm_info(get_type_name(), {"req item",req.sprint}, UVM_HIGH)
      do_drive();
      seq_item_port.item_done();
    end
  endtask : run_phase

//=====================================================

  task do_drive();
    string seq_name;
    int    seq_var;
    string seq_mode;

    `uvm_info(get_type_name(), {"register_driver::do_drive task start"}, UVM_HIGH); //  UVM_HIGH  UVM_MEDIUM

    // If called while the reset ist activ, drive the reset input values
    if (vif.rst_n == 0) begin
        //disable xy
      reset_values();               // drive the reset values
      @(posedge vif.rst_n);
        //set vif.xy
    end

      // take the controll values from the item
      seq_name = req.seq_name;
      seq_var  = req.seq_var;
      seq_mode = req.seq_mode;

      // Check which task is requested by the sequencer and call it!
      if (seq_name) case (seq_name)

        "passive_reset"     : passive_reset(seq_var);
        "active_reset"      : active_reset(seq_var);
        "register_init_seq" : register_init_seq();
        "set_signals"       : set_signals(seq_var);
        default: `uvm_error(get_type_name(), $sformatf("Illegal sequence type %s !!",seq_name))
      endcase

  endtask

//=====================================================

//function void set_mode(int value);
//  vif.mode = value;
//  //$display("mode ",vif.mode);
//endfunction

  function void set_signals(int value);

    vif.config_reg  = req.config_reg ;
    
  endfunction

//=====================================================
// Drive default the expected reset values or
// for test purpose random data

  function void reset_values(int rndm = 0);
    //disable clk_driver;
    if (rndm==0)
      begin
        `uvm_info(get_type_name(), {"register_driver::reset_values start"}, UVM_HIGH);
        
        //vif.i_signal = 0 ;
        vif.config_reg  = '0 ;
        
      end
   else
      begin
      
        //vif.i_signal = $urandom();//$urandom_range(von,bis);
        vif.config_reg  = $urandom();
        
      end

//    fork
//      begin
//        @(posedge vif.rst_n);
//        //vif.reset_xyz_n = '1 ;
//        clk_driver();
//      end
//    join_none

  endfunction

//=====================================================

  task register_init_seq();
    //@(posedge vif.clk);
    //vif.input_signal  = req.input_signal;
    //analysis_port.write(req);
    //#wait time;
  endtask

//=====================================================

  task active_reset(int rndm = 0);
      int d = $urandom_range(SYSTEM_CLK_PERIOD,SYSTEM_CLK_PERIOD*5);  
      int s = $urandom_range(0,SYSTEM_CLK_PERIOD);
      @(posedge vif.clk);
      #(s * 1ns);

      vif.rst_n = 0;
      reset_values(rndm);               // drive the reset values

      #(d * 1ns);
      vif.rst_n = 1;

      if (rndm==0) `uvm_info(get_type_name(), {"register_driver::reset done"}, UVM_HIGH);
  endtask

  task passive_reset(int rndm = 0);
    disable psv_rst;
    psv_rst:
    fork
      forever 
      begin
        if (vif.rst_n == 1) @(negedge vif.rst_n);
        reset_values(rndm);               // drive the reset values
        @(posedge vif.rst_n);
        if (rndm==0) `uvm_info(get_type_name(), {"register_driver::reset done"}, UVM_HIGH);
      end
    join_none      
  endtask

//=====================================================

//  task new_task_or_req();
//    string test_name = "new_task_or_req";
//    `uvm_info(get_type_name(), {$sformatf("register_driver::%s start",test_name)}, UVM_HIGH);
//
//    //@(posedge vif.clk);
//    //vif.input_signal   = req.input_signal ;
//
//    `uvm_info(get_type_name(), {$sformatf("register_driver::%s finished",test_name)}, UVM_HIGH);
//  endtask

//=====================================================
