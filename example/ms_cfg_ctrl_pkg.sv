//generated ms_cfg_ctrl_pkg.sv

`include "../dut/common_defines.sv"

package ms_cfg_ctrl_pkg;

  const time SYSTEM_CLK_PERIOD = 20ns;

  const logic  [8-1:0]  rst_ma_send_data = '0; //  ['master_if_0']
  const logic  [3:0]    rst_ma_sel       = '0; //  ['master_if_0']
  const logic           rst_ma_enable    = '0; //  ['master_if_0']
  const logic  [8-1:0]  rst_sl_send_data = '0; //  ['slave_if_0']
  const logic  [16-1:0] rst_config_data  = '0; //  ['target_if_0']

endpackage : ms_cfg_ctrl_pkg
