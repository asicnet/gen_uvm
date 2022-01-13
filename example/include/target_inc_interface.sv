
  `include "uvm_macros.svh"
  import uvm_pkg::*;
  string if_name = "target_if";

  target_item resp;
  target_monitor proxy_back_ptr;
  //event target_end;
  //time t,t0,t1;

  int SB  = 0;
  int COV = 1;

  default clocking cp @(posedge clk); endclocking
  // always \@(reset) begin rst_n = reset; end
  //  RST_SIGNAL_assert :  assert property ( PROPERTY ) `uvm_error(if_name,$sformatf("Concurrent Assertion  %0s  failed  >> %0s","RST_SIGNAL", "MSG"));  
 
  RST_CONFIG_DATA_assert: assert property ( @(posedge rst_n) (config_data == rst_config_data ) )  else `uvm_error( if_name,$sformatf("config_data -> reset value incorrect 0x%04h", $sampled(config_data)))


  // Interface Ports:

  //  logic  [16-1:0] config_data ; // out := '0

        
    always_comb 
      if(rst_n)
      begin     
        automatic target_item resp = target_item::type_id::create("resp");

         resp.target       = COV         ;

         resp.config_data  = config_data ;

        
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
  