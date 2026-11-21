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
void car_err_fun(double *nom_x, double *delta_x, double *out_351073186439356103);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1747083980238712734);
void car_H_mod_fun(double *state, double *out_6472911724186297456);
void car_f_fun(double *state, double dt, double *out_4383029369194465735);
void car_F_fun(double *state, double dt, double *out_1598730726278697242);
void car_h_25(double *state, double *unused, double *out_6820208747041345332);
void car_H_25(double *state, double *unused, double *out_9109468649201723650);
void car_h_24(double *state, double *unused, double *out_6116379550706621676);
void car_H_24(double *state, double *unused, double *out_3298083018178946685);
void car_h_30(double *state, double *unused, double *out_1061063903712703853);
void car_H_30(double *state, double *unused, double *out_9207936477364587896);
void car_h_26(double *state, double *unused, double *out_3940609363948141792);
void car_H_26(double *state, double *unused, double *out_5595772105633771742);
void car_h_27(double *state, double *unused, double *out_6216892862364867815);
void car_H_27(double *state, double *unused, double *out_7033173165564162985);
void car_h_29(double *state, double *unused, double *out_2579443334110845465);
void car_H_29(double *state, double *unused, double *out_5319810438694611952);
void car_h_28(double *state, double *unused, double *out_7160402715266530250);
void car_H_28(double *state, double *unused, double *out_7283440710259938203);
void car_h_31(double *state, double *unused, double *out_8678809336312721323);
void car_H_31(double *state, double *unused, double *out_9078822687324763222);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}