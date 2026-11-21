#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7083424895904025255);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6838748995040044771);
void pose_H_mod_fun(double *state, double *out_1547699279302149631);
void pose_f_fun(double *state, double dt, double *out_6474378312856621026);
void pose_F_fun(double *state, double dt, double *out_8540366478724720162);
void pose_h_4(double *state, double *unused, double *out_1356905819811932649);
void pose_H_4(double *state, double *unused, double *out_793538277247437024);
void pose_h_10(double *state, double *unused, double *out_5351520755944402824);
void pose_H_10(double *state, double *unused, double *out_1794142950195422749);
void pose_h_13(double *state, double *unused, double *out_6629156441156146262);
void pose_H_13(double *state, double *unused, double *out_6817092931069263905);
void pose_h_14(double *state, double *unused, double *out_2949760970451347774);
void pose_H_14(double *state, double *unused, double *out_3169702579092047505);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}