#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_872186578222559432);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6152122967198108302);
void car_H_mod_fun(double *state, double *out_3894145102241659448);
void car_f_fun(double *state, double dt, double *out_2609582718362600052);
void car_F_fun(double *state, double dt, double *out_3593638983953165378);
void car_h_25(double *state, double *unused, double *out_1355225652381008580);
void car_H_25(double *state, double *unused, double *out_1009546722943005392);
void car_h_24(double *state, double *unused, double *out_7563426264467864558);
void car_H_24(double *state, double *unused, double *out_3186761146550155365);
void car_h_30(double *state, double *unused, double *out_9118490909201681021);
void car_H_30(double *state, double *unused, double *out_3527879681450254019);
void car_h_26(double *state, double *unused, double *out_4326579896847024950);
void car_H_26(double *state, double *unused, double *out_2731956595931050832);
void car_h_27(double *state, double *unused, double *out_6672887729589146357);
void car_H_27(double *state, double *unused, double *out_1294555536000659589);
void car_h_29(double *state, double *unused, double *out_3892583693366356074);
void car_H_29(double *state, double *unused, double *out_3007918262870210622);
void car_h_28(double *state, double *unused, double *out_1710507731907853125);
void car_H_28(double *state, double *unused, double *out_1044287991304884371);
void car_h_31(double *state, double *unused, double *out_5415609573969342356);
void car_H_31(double *state, double *unused, double *out_3358164698164402308);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}