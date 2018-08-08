import asm_utils

def vm_valid_command(line):
    line = line.strip()
    instrs = ["push", "pop", "add", "sub", "label", "goto", "if-goto", "eq", "lt", "gt", "neg", "or", "not", "function", "call"]
    find = line.find(" ")
    if find == -1:
        find = len(line)

    find = max(find, 3)
    instr  = line[0:find]
    return instr in instrs and (not line.startswith(";"))

def vm_command_line(list_commands_pos, list_comments_pos, list_labels_pos, pc_counter):
    file_line = asm_utils.z01_real_line(list_comments_pos, pc_counter) # obtem apontador do arquivo sem comentarios
    a = len([i for i in list_commands_pos if i <= file_line]) # verifica quantos comandos ja ocorreu com base na linha
    a = a - 1 # fix first command
    a = a + asm_utils.z01_label_count(list_labels_pos, a) # pula labels
    if a < 0:
        a = 0
    return a

def vm_global_stack_name(pos):
    return pos + 256