-- Elementos de Sistemas
-- by Luciano Soares
-- inversor16.vhd

library IEEE;
use IEEE.STD_LOGIC_1164.all;

entity inversor16 is
   port(z   : in STD_LOGIC;
	     a   : in STD_LOGIC_VECTOR(15 downto 0);
        y   : out STD_LOGIC_VECTOR(15 downto 0)
   );
end entity;

architecture rtl of inversor16 is
begin
	y(0) <= z xor a(0);
	y(1) <= z xor a(1);
	y(2) <= z xor a(2);
	y(3) <= z xor a(3);
	y(4) <= z xor a(4);
	y(5) <= z xor a(5);
	y(6) <= z xor a(6);
	y(7) <= z xor a(7);
	y(8) <= z xor a(8);
	y(9) <= z xor a(9);
	y(10) <= z xor a(10);
	y(11) <= z xor a(11);
	y(12) <= z xor a(12);
	y(13) <= z xor a(13);
	y(14) <= z xor a(14);
	y(15) <= z xor a(15);
end architecture;
