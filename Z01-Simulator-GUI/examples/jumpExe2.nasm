	;; Elementos De Sistemas
	;; Eng. Insper - Rafael Corsi
	;; Exemplo de salto condicional
	;;
	;; s = 0
   ;; d = 0
	;; while(D < 2)
	;;  s = s+1
   ;;  d = d+1

INICIO:
  leaw $0, %A
  movw %A, %S                   ; Carrega 0 em S
  leaw $2, %A
  movw %A, %D                   ; Carrega 2 em D

WHILE:
  leaw $END, %A
  je %D                         ; Salta se D == 0
  nop

  incw %S                       ; Incrementa S
  decw %D                       ; Decrementa D
  leaw $WHILE, %A
  jmp                           ; Salto incondicional
  nop                           ; No-Operation
                                ; (necessário após jump)

END:                            ; Loop infinito
  
