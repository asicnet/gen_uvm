
library IEEE;
use IEEE.std_Logic_1164.all;
use IEEE.numeric_std.all;

entity ms_cfg_ctrl is
  generic ( 
     g_data_width : integer:= 8;
     g_conf_width : integer:= 16
    );
  port (
    clock          : in  std_logic ;
    reset          : in  std_logic ;
    --master         
    ma_get_data    : in  std_logic_vector(g_data_width-1 downto 0) ;
    ma_send_data   : out std_logic_vector(g_data_width-1 downto 0) ;
    o_sel          : out std_logic_vector(3 downto 0)              ;
    o_enable       : out std_logic ;      
    --slave              
    sl_get_data    : in  std_logic_vector(g_data_width-1 downto 0) ;
    sl_send_data   : out std_logic_vector(g_data_width-1 downto 0) ;
    sel            : in  std_logic_vector(3 downto 0)              ;
    enable         : in  std_logic ;
    --target       :    
    o_config_data  : out std_logic_vector(g_conf_width-1 downto 0) ;
    reg_data       : in  std_logic_vector(7 downto 0)  
  );
end;

architecture rtl of ms_cfg_ctrl is

begin

    ma_send_data   <= (others => '0') ;
    o_sel          <= (others => '0') ;
    sl_send_data   <= (others => '0') ;
    o_config_data  <= (others => '0') ;
                   
    o_enable       <= '0' ;
 
end;  
