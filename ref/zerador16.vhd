-- Elementos de Sistemas
-- by Luciano Soares
-- zerador16.vhd

library IEEE;
use IEEE.STD_LOGIC_1164.all;

entity zerador16 is
   port(z   : in STD_LOGIC;
	      a   : in STD_LOGIC_VECTOR(15 downto 0);
        y   : out STD_LOGIC_VECTOR(15 downto 0)
   );
end zerador16;

architecture rtl of zerador16 is
signal notz: std_logic;
begin

	notz <= not z;
	y(0) <= notz and a(0);
	y(1) <= notz and a(1);
	y(2) <= notz and a(2);
	y(3) <= notz and a(3);
	y(4) <= notz and a(4);
	y(5) <= notz and a(5);
	y(6) <= notz and a(6);
	y(7) <= notz and a(7);
	y(8) <= notz and a(8);
	y(9) <= notz and a(9);
	y(10) <= notz and a(10);
	y(11) <= notz and a(11);
	y(12) <= notz and a(12);
	y(13) <= notz and a(13);
	y(14) <= notz and a(14);
	y(15) <= notz and a(15);
end architecture;
