
  `include "uvm_macros.svh"
  import uvm_pkg::*;
  string if_name = "register_if";

  register_item resp;
  register_monitor proxy_back_ptr;
  //event register_end;
  //time t,t0,t1;

  int SB  = 0;
  int COV = 1;

  default clocking cp @(posedge clk); endclocking
  // always \@(reset) begin rst_n = reset; end
  //  RST_SIGNAL_assert :  assert property ( PROPERTY ) `uvm_error(if_name,$sformatf("Concurrent Assertion  %0s  failed  >> %0s","RST_SIGNAL", "MSG"));  
 


  // Interface Ports:

  //  logic  [7:0] config_reg ; // in := '0

        
    always_comb 
      if(rst_n)
      begin     
        automatic register_item resp = register_item::type_id::create("resp");

         resp.target      = COV        ;

         resp.config_reg  = config_reg ;

        
        proxy_back_ptr.write(resp);
      end  

  // always_ff @(posedge clk_50 iff rst_n or negedge rst_n)
  //   if(rst_n)
  //   begin 
  //     signal_d <= i_signal;
  //     if (signal_d == 0 && i_signal == 1)
  //       outsig = 1;
  //     else
  //       outsig = 0;      
  //   end 
  //   else
  //     outsig = 0;
  
