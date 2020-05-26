-- Elementos de Sistemas
-- by Luciano Soares
-- And16.vhd

library IEEE;
use IEEE.STD_LOGIC_1164.all;

entity And16 is
	port (
			a:   in  STD_LOGIC_VECTOR(15 downto 0);
			b:   in  STD_LOGIC_VECTOR(15 downto 0);
			q:   out STD_LOGIC_VECTOR(15 downto 0));
end entity;

architecture arch of And16 is
begin
	q <= a and b;
end architecture;
