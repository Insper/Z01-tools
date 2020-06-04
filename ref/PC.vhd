-- Elementos de Sistemas
-- developed by Luciano Soares
-- file: PC.vhd
-- date: 4/4/2017

-- Contador de 16bits
-- if (reset[t] == 1) out[t+1] = 0
-- else if (load[t] == 1)  out[t+1] = in[t]
-- else if (inc[t] == 1) out[t+1] = out[t] + 1
-- else out[t+1] = out[t]

library ieee;
use ieee.std_logic_1164.all;
use IEEE.NUMERIC_STD.ALL;

entity PC is
    port(
        clock     : in  STD_LOGIC;
        increment : in  STD_LOGIC;
        load      : in  STD_LOGIC;
        reset     : in  STD_LOGIC;
        input     : in  STD_LOGIC_VECTOR(15 downto 0);
        output    : out STD_LOGIC_VECTOR(15 downto 0)
    );
end entity;

architecture arch of PC is

 signal muxOut : std_logic_vector(15 downto 0);

  component Inc16 is
      port(
          a   :  in STD_LOGIC_VECTOR(15 downto 0);
          q   : out STD_LOGIC_VECTOR(15 downto 0)
          );
  end component;

  component Register8 is
      port(
          clock:   in STD_LOGIC;
          input:   in STD_LOGIC_VECTOR(7 downto 0);
          load:    in STD_LOGIC;
          output: out STD_LOGIC_VECTOR(7 downto 0)
        );
    end component;

begin

	process(clock,reset)
		variable count : STD_LOGIC_VECTOR(15 downto 0) := "0000000000000000";
	begin
		if rising_edge(clock) then
   			if reset = '1' then
    			count := (others => '0');
   			elsif load = '1' then
	  			count := STD_LOGIC_VECTOR(to_unsigned(to_integer(unsigned(input)), 16));
	 		elsif increment = '1' then
				count := STD_LOGIC_VECTOR(to_unsigned(to_integer(unsigned( count )) + 1, 16));
	  		end if;
	 	end if;
		output <= count;
	end process;

end architecture;
