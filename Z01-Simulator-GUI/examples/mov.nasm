; Elementos de Sistemas : 2018a
; Rafael Corsi
; Hardware : Z0.1
;
; Data :
;    - Dez 2018
; Descrição :
;    - Testa movimentação de dados entre registradores e
;      entre memória (mov)

; -----------------------
; Mov A -> D
; Mov D -> (A)
; output : RAM[0] = 5
; -----------------------
  leaw $5, %A
  movw %A, %D
  leaw %0, %A
  movw %D, (%A)

; -----------------------
; Mov A -> D
; Mov D -> S
; Mov S -> (A)
; output : RAM[1] = 6
; -----------------------
  leaw $6, %A
  movw %A, %D
  movw %D, %S
  leaw %1, %A
  movw %S, (%A)

; -----------------------
; Mov A -> S
; Mov S -> (A)
; output : RAM 2 = 7
; -----------------------
  leaw %7, %A
  movw %A, %S
  leaw %2, %A
  movw %S, (%A)

; -----------------------
; mov (A) -> D
  leaw %5, %A
  movw (%A), %D

; -----------------------
; mov (A) -> S
  leaw %5, %A
  movw (%A), %S

