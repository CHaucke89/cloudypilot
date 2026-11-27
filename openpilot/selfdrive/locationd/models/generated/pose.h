#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5456529213378525094);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5389676744893681967);
void pose_H_mod_fun(double *state, double *out_6025654641358348591);
void pose_f_fun(double *state, double dt, double *out_8477885110547017436);
void pose_F_fun(double *state, double dt, double *out_4130905704562196471);
void pose_h_4(double *state, double *unused, double *out_3512950417453688471);
void pose_H_4(double *state, double *unused, double *out_7223602123241246695);
void pose_h_10(double *state, double *unused, double *out_9200925151251471853);
void pose_H_10(double *state, double *unused, double *out_3716827504774369733);
void pose_h_13(double *state, double *unused, double *out_7407158574033381569);
void pose_H_13(double *state, double *unused, double *out_3389846659938722671);
void pose_h_14(double *state, double *unused, double *out_5563746504250402940);
void pose_H_14(double *state, double *unused, double *out_4140813690945874399);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}