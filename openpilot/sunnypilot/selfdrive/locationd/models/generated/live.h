#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_498540792853724902);
void live_err_fun(double *nom_x, double *delta_x, double *out_6703113282882877442);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8674024043891081709);
void live_H_mod_fun(double *state, double *out_7893631122165334988);
void live_f_fun(double *state, double dt, double *out_7381276684069395384);
void live_F_fun(double *state, double dt, double *out_5127154685982997860);
void live_h_4(double *state, double *unused, double *out_2412710146794118289);
void live_H_4(double *state, double *unused, double *out_6073918121923380634);
void live_h_9(double *state, double *unused, double *out_3786524990200062270);
void live_H_9(double *state, double *unused, double *out_1213300813341066836);
void live_h_10(double *state, double *unused, double *out_2962484940083472728);
void live_H_10(double *state, double *unused, double *out_1578870585781044341);
void live_h_12(double *state, double *unused, double *out_7457163599535631723);
void live_H_12(double *state, double *unused, double *out_5991567574743437986);
void live_h_35(double *state, double *unused, double *out_6394423511583937209);
void live_H_35(double *state, double *unused, double *out_1691101318433594870);
void live_h_32(double *state, double *unused, double *out_6145755598937304786);
void live_H_32(double *state, double *unused, double *out_1822266103374335339);
void live_h_13(double *state, double *unused, double *out_2862531200562713871);
void live_H_13(double *state, double *unused, double *out_751115108243379849);
void live_h_14(double *state, double *unused, double *out_3786524990200062270);
void live_H_14(double *state, double *unused, double *out_1213300813341066836);
void live_h_33(double *state, double *unused, double *out_396984252282881968);
void live_H_33(double *state, double *unused, double *out_6559056462002242317);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}