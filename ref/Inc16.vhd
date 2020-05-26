-- Elementos de Sistemas
-- by Luciano Soares
-- Inc16.vhd

-- Incrementador de 16 bits
-- adiciona 1 ao valore de entrada (adição aritmética)

library IEEE;
use IEEE.STD_LOGIC_1164.all;

entity Inc16 is
	port(
		a   :  in STD_LOGIC_VECTOR(15 downto 0);
		q   : out STD_LOGIC_VECTOR(15 downto 0)
	);
end entity;

architecture rtl of Inc16 is

component HalfAdder is
	port(
		a,b:        in STD_LOGIC;   -- entradas
		soma,vaium: out STD_LOGIC   -- sum e carry
	);
end component;

signal s: std_logic_vector(14 downto 0);

begin
	u0  : HalfAdder port map ( a(0),  '1', q(0), s(0));
	u1  : HalfAdder port map ( a(1), s(0), q(1), s(1));
	u2  : HalfAdder port map ( a(2), s(1), q(2), s(2));
	u3  : HalfAdder port map ( a(3), s(2), q(3), s(3));
	u4  : HalfAdder port map ( a(4), s(3), q(4), s(4));
	u5  : HalfAdder port map ( a(5), s(4), q(5), s(5));
	u6  : HalfAdder port map ( a(6), s(5), q(6), s(6));
	u7  : HalfAdder port map ( a(7), s(6), q(7), s(7));
	u8  : HalfAdder port map ( a(8), s(7), q(8), s(8));
	u9  : HalfAdder port map ( a(9), s(8), q(9), s(9));
	u10 : HalfAdder port map (a(10), s(9),q(10),s(10));
	u11 : HalfAdder port map (a(11),s(10),q(11),s(11));
	u12 : HalfAdder port map (a(12),s(11),q(12),s(12));
	u13 : HalfAdder port map (a(13),s(12),q(13),s(13));
	u14 : HalfAdder port map (a(14),s(13),q(14),s(14));
	u15 : HalfAdder port map (a(15),s(14),q(15),open);
end architecture;
