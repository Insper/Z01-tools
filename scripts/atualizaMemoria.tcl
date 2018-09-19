# Load Quartus Prime Tcl Package
package require  ::quartus::insystem_memory_edit

puts stdout ""
puts stdout "Funciona somente com o quartus_stp"
puts stdout ""

set DEV_NAME "@1: 5CE(BA4|FA4) (0x02B050DD)"

set MIF "/home/corsi/Dropbox/Insper/3s-ElementoDeSistemas/5-Repositorios/Z01.1-priv/Projetos/src/bin/hack/testeSW.mif"

set JTAG "USB-Blaster \[1-3\]"

begin_memory_edit -hardware_name $JTAG -device_name $DEV_NAME

update_content_to_memory_from_file -instance_index 0 -mem_file_path $MIF -mem_file_type "mif"

end_memory_edit;
