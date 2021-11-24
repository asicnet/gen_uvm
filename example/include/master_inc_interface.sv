
  `include "uvm_macros.svh"
  import uvm_pkg::*;
  string if_name = "master_if";

  master_item resp;
  master_monitor proxy_back_ptr;
  //event master_end;
  //time t,t0,t1;

  int SB  = 0;
  int COV = 1;

  default clocking cp @(posedge clk); endclocking
  // always \@(reset) begin rst_n = reset; end
  //  RST_SIGNAL_assert :  assert property ( PROPERTY ) `uvm_error(if_name,$sformatf("Concurrent Assertion  %0s  failed  >> %0s","RST_SIGNAL", "MSG"));  
 
  RST_MA_SEND_DATA_assert: assert property ( @(posedge rst_n) (ma_send_data == rst_ma_send_data ) )  else `uvm_error( if_name,$sformatf("ma_send_data -> reset value incorrect 0x%04h", $sampled(ma_send_data)))
  RST_MA_SEL_assert:       assert property ( @(posedge rst_n) (ma_sel == rst_ma_sel ) )              else `uvm_error( if_name,$sformatf("ma_sel -> reset value incorrect 0x%04h", $sampled(ma_sel)))
  RST_MA_ENABLE_assert:    assert property ( @(posedge rst_n) (ma_enable == rst_ma_enable ) )        else `uvm_error( if_name,$sformatf("ma_enable -> reset value incorrect 0x%04h", $sampled(ma_enable)))


  // Interface Ports:

  //  logic  [8-1:0] ma_get_data  ; // in  := '0
  //  logic  [8-1:0] ma_send_data ; // out := '0
  //  logic  [3:0]   ma_sel       ; // out := '0
  //  logic          ma_enable    ; // out := '0

        
    always_comb 
      if(rst_n)
      begin     
        automatic master_item resp = master_item::type_id::create("resp");

         resp.target        = COV          ;

         resp.ma_get_data   = ma_get_data  ;
         resp.ma_send_data  = ma_send_data ;
         resp.ma_sel        = ma_sel       ;
         resp.ma_enable     = ma_enable    ;

        
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
  
