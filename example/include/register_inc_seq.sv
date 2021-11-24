
`ifndef REGISTER_SEQ_SV
`define REGISTER_SEQ_SV

class register_test_seq extends register_default_seq;

  `uvm_object_utils(register_test_seq)

  string test_name;
  string reset_type = "passive_reset";  // passive_reset or active_reset

  function new(string name = "");
    super.new(name);
  endfunction : new

//=====================================================

  task body();

    if ( !uvm_config_db#(register_config)::get(get_sequencer(), "", "config", m_config) )
      `uvm_error(get_type_name(), "Failed to get config object")

    begin

      case (test_name)

        "RESET_VALUES"         : reset_driver     (reset_type);
        "SET_SIGNALS"          : set_signals      ("set_signals");

        default: `uvm_fatal(get_type_name(), $sformatf("Illegal test_name name %s",test_name))
      endcase
    end

    `uvm_info(get_type_name(), "register_test_seq sequence completed\n", UVM_MEDIUM)

  endtask : body



  task get_item(output register_item mreq, input string seq_name = "");

      mreq = register_item::type_id::create("req");
      mreq.init_item();
      mreq.seq_name = seq_name;
      start_item(mreq);

  endtask

//=====================================================

task reset_driver(string seq_name="passive_reset", int rndm = 0);
    string task_name = "reset_driver";

      get_item(req,seq_name);
        req.seq_var  = rndm;
        if (rndm)
          req.randomize();
        else begin
          //req.xyz  = '0;
        end
      finish_item(req);

  endtask

//========================================================
// TEST set_signals
//

  task set_signals(string seq_name, int rndm = 0,int seq_var = 0);
    string task_name = "set_signals";

    reset_driver(reset_type);                // test start always with reset

    for (int value=0; value<100; value++)
    begin
        get_item(req,seq_name);
          begin
            req.seq_var = seq_var;

            req.config_reg  = value%2;
       
          end
        finish_item(req);
        #SYSTEM_CLK_PERIOD;
    end

  endtask

//==========================================================================================================

endclass : register_test_seq

`endif // REGISTER_SEQ_SV
