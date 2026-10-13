; Space Invaders program for AktuellerStand.circ
; Tile / sprite ids:
;   0 empty / black
;   1 player
;   2 green enemy
;   3 red enemy
;   4 shot
; r0 = empty
; r1 = player
; r2 = green enemy
; r3 = red enemy
; r4 = shot / input scratch
; r5 = zero for stable JUMPS
; r6 = comparison scratch
; r7 = raw input

MOV0L r0, #0
MOV0L r1, #1
MOV0L r2, #2
MOV0L r3, #3
MOV0L r4, #4
MOV0L r5, #0
MOV0L r6, #0
MOV0L r7, #0

boot:
OUT r2, #0
OUT r3, #1
OUT r2, #2
OUT r3, #3
OUT r3, #4
OUT r2, #5
OUT r3, #6
OUT r2, #7
OUT r0, #8
OUT r0, #9
OUT r4, #10
OUT r0, #11
OUT r0, #12
OUT r1, #13
OUT r0, #14
OUT r0, #15
JUMPS r5, main_loop

; --- main loop -----------------------------------------------------------------
main_loop:
IN r7, #6

; if input == 1, player left
MOV r6, r7
SUB r6, #1
JZ render_left

; if input == 2, player right
MOV r6, r7
SUB r6, #2
JZ render_right

; if input == 4, shoot and win
MOV r6, r7
SUB r6, #4
JZ render_shoot_win

; if input == 5, left + shoot
MOV r6, r7
SUB r6, #5
JZ render_left_shoot_win

; if input == 6, right + shoot
MOV r6, r7
SUB r6, #6
JZ render_right_shoot_win

; default: center
JUMPS r5, render_center

render_center:
OUT r2, #0
OUT r3, #1
OUT r2, #2
OUT r3, #3
OUT r3, #4
OUT r2, #5
OUT r3, #6
OUT r2, #7
OUT r0, #8
OUT r0, #9
OUT r4, #10
OUT r0, #11
OUT r0, #12
OUT r1, #13
OUT r0, #14
OUT r0, #15
JUMPS r5, main_loop

render_left:
OUT r2, #0
OUT r3, #1
OUT r2, #2
OUT r3, #3
OUT r3, #4
OUT r2, #5
OUT r3, #6
OUT r2, #7
OUT r0, #8
OUT r0, #9
OUT r4, #10
OUT r0, #11
OUT r1, #12
OUT r0, #13
OUT r0, #14
OUT r0, #15
JUMPS r5, main_loop

render_right:
OUT r2, #0
OUT r3, #1
OUT r2, #2
OUT r3, #3
OUT r3, #4
OUT r2, #5
OUT r3, #6
OUT r2, #7
OUT r0, #8
OUT r0, #9
OUT r4, #10
OUT r0, #11
OUT r0, #12
OUT r0, #13
OUT r1, #14
OUT r0, #15
JUMPS r5, main_loop

render_shoot_win:
OUT r0, #0
OUT r0, #1
OUT r4, #2
OUT r0, #3
OUT r0, #4
OUT r0, #5
OUT r4, #6
OUT r0, #7
OUT r0, #8
OUT r0, #9
OUT r4, #10
OUT r0, #11
OUT r0, #12
OUT r1, #13
OUT r0, #14
OUT r0, #15
JUMPS r5, win_loop

render_left_shoot_win:
OUT r4, #0
OUT r0, #1
OUT r0, #2
OUT r0, #3
OUT r4, #4
OUT r0, #5
OUT r0, #6
OUT r0, #7
OUT r4, #8
OUT r0, #9
OUT r0, #10
OUT r0, #11
OUT r1, #12
OUT r0, #13
OUT r0, #14
OUT r0, #15
JUMPS r5, win_loop

render_right_shoot_win:
OUT r0, #0
OUT r0, #1
OUT r4, #2
OUT r0, #3
OUT r0, #4
OUT r0, #5
OUT r4, #6
OUT r0, #7
OUT r0, #8
OUT r0, #9
OUT r4, #10
OUT r0, #11
OUT r0, #12
OUT r0, #13
OUT r1, #14
OUT r0, #15
JUMPS r5, win_loop

; --- win loop ------------------------------------------------------------------
win_loop:
OUT r4, #0
OUT r0, #1
OUT r4, #2
OUT r0, #3
OUT r0, #4
OUT r4, #5
OUT r0, #6
OUT r4, #7
OUT r4, #8
OUT r0, #9
OUT r4, #10
OUT r0, #11
OUT r0, #12
OUT r4, #13
OUT r0, #14
OUT r4, #15

OUT r4, #0
OUT r0, #1
OUT r4, #2
OUT r0, #3
OUT r0, #4
OUT r4, #5
OUT r0, #6
OUT r4, #7
OUT r4, #8
OUT r0, #9
OUT r4, #10
OUT r0, #11
OUT r0, #12
OUT r4, #13
OUT r0, #14
OUT r4, #15

OUT r0, #0
OUT r4, #1
OUT r0, #2
OUT r4, #3
OUT r4, #4
OUT r0, #5
OUT r4, #6
OUT r0, #7
OUT r0, #8
OUT r4, #9
OUT r0, #10
OUT r4, #11
OUT r4, #12
OUT r0, #13
OUT r4, #14
OUT r0, #15
JUMPS r5, win_loop
