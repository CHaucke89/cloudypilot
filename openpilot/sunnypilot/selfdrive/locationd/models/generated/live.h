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
void live_H(double *in_vec, double *out_4117915229677533295);
void live_err_fun(double *nom_x, double *delta_x, double *out_1111728286692110734);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_5480592812120928369);
void live_H_mod_fun(double *state, double *out_844583164805840257);
void live_f_fun(double *state, double dt, double *out_899759543201008461);
void live_F_fun(double *state, double dt, double *out_856353790376260345);
void live_h_4(double *state, double *unused, double *out_623600002588685496);
void live_H_4(double *state, double *unused, double *out_6042830999115724269);
void live_h_9(double *state, double *unused, double *out_4793606516299583490);
void live_H_9(double *state, double *unused, double *out_5116694139329379877);
void live_h_10(double *state, double *unused, double *out_6052409832948229162);
void live_H_10(double *state, double *unused, double *out_4766607586097393258);
void live_h_12(double *state, double *unused, double *out_2225586786285333876);
void live_H_12(double *state, double *unused, double *out_338427377927008727);
void live_h_35(double *state, double *unused, double *out_3878021416408211374);
void live_H_35(double *state, double *unused, double *out_1991221728586363146);
void live_h_32(double *state, double *unused, double *out_5704871162506131118);
void live_H_32(double *state, double *unused, double *out_7664444319142924608);
void live_h_13(double *state, double *unused, double *out_4873250532339654315);
void live_H_13(double *state, double *unused, double *out_545614415682971943);
void live_h_14(double *state, double *unused, double *out_4793606516299583490);
void live_H_14(double *state, double *unused, double *out_5116694139329379877);
void live_h_33(double *state, double *unused, double *out_3639668649367077203);
void live_H_33(double *state, double *unused, double *out_1159335276052494458);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}