library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity impressora is
	port (
    SW1,SW2,SW3,SW4 : in  STD_LOGIC;
    x : out STD_LOGIC );
end entity;

architecture arch of impressora is

begin

  x <= (sw1 and sw2) or (sw1 and sw3) or (sw2 and sw3) or (sw2 and sw4) or (sw3 and sw4);

end architecture;
