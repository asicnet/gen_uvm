
  `include "uvm_macros.svh"
  import uvm_pkg::*;
  string if_name = "slave_if";

  slave_item resp;
  slave_monitor proxy_back_ptr;
  //event slave_end;
  //time t,t0,t1;

  int SB  = 0;
  int COV = 1;

  default clocking cp @(posedge clk); endclocking
  // always \@(reset) begin rst_n = reset; end
  //  RST_SIGNAL_assert :  assert property ( PROPERTY ) `uvm_error(if_name,$sformatf("Concurrent Assertion  %0s  failed  >> %0s","RST_SIGNAL", "MSG"));  
 
  RST_SL_SEND_DATA_assert: assert property ( @(posedge rst_n) (sl_send_data == rst_sl_send_data ) )  else `uvm_error( if_name,$sformatf("sl_send_data -> reset value incorrect 0x%04h", $sampled(sl_send_data)))


  // Interface Ports:

  //  logic  [8-1:0] sl_get_data  ; // in  := '0
  //  logic  [8-1:0] sl_send_data ; // out := '0
  //  logic  [3:0]   sl_sel       ; // in  := '0
  //  logic          sl_enable    ; // in  := '0

        
    always_comb 
      if(rst_n)
      begin     
        automatic slave_item resp = slave_item::type_id::create("resp");

         resp.target        = COV          ;

         resp.sl_get_data   = sl_get_data  ;
         resp.sl_send_data  = sl_send_data ;
         resp.sl_sel        = sl_sel       ;
         resp.sl_enable     = sl_enable    ;

        
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
  
