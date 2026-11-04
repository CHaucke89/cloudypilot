#include "car.h"

namespace {
#define DIM 9
#define EDIM 9
#define MEDIM 9
typedef void (*Hfun)(double *, double *, double *);

double rotational_inertia;

void set_rotational_inertia(double x){ rotational_inertia = x;}

double center_to_front;

void set_center_to_front(double x){ center_to_front = x;}

double center_to_rear;

void set_center_to_rear(double x){ center_to_rear = x;}

double stiffness_front;

void set_stiffness_front(double x){ stiffness_front = x;}

double stiffness_rear;

void set_stiffness_rear(double x){ stiffness_rear = x;}
const static double MAHA_THRESH_25 = 3.8414588206941227;
const static double MAHA_THRESH_24 = 5.991464547107981;
const static double MAHA_THRESH_30 = 3.8414588206941227;
const static double MAHA_THRESH_26 = 3.8414588206941227;
const static double MAHA_THRESH_27 = 3.8414588206941227;
const static double MAHA_THRESH_29 = 3.8414588206941227;
const static double MAHA_THRESH_28 = 3.8414588206941227;
const static double MAHA_THRESH_31 = 3.8414588206941227;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_351073186439356103) {
   out_351073186439356103[0] = delta_x[0] + nom_x[0];
   out_351073186439356103[1] = delta_x[1] + nom_x[1];
   out_351073186439356103[2] = delta_x[2] + nom_x[2];
   out_351073186439356103[3] = delta_x[3] + nom_x[3];
   out_351073186439356103[4] = delta_x[4] + nom_x[4];
   out_351073186439356103[5] = delta_x[5] + nom_x[5];
   out_351073186439356103[6] = delta_x[6] + nom_x[6];
   out_351073186439356103[7] = delta_x[7] + nom_x[7];
   out_351073186439356103[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_1747083980238712734) {
   out_1747083980238712734[0] = -nom_x[0] + true_x[0];
   out_1747083980238712734[1] = -nom_x[1] + true_x[1];
   out_1747083980238712734[2] = -nom_x[2] + true_x[2];
   out_1747083980238712734[3] = -nom_x[3] + true_x[3];
   out_1747083980238712734[4] = -nom_x[4] + true_x[4];
   out_1747083980238712734[5] = -nom_x[5] + true_x[5];
   out_1747083980238712734[6] = -nom_x[6] + true_x[6];
   out_1747083980238712734[7] = -nom_x[7] + true_x[7];
   out_1747083980238712734[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_6472911724186297456) {
   out_6472911724186297456[0] = 1.0;
   out_6472911724186297456[1] = 0.0;
   out_6472911724186297456[2] = 0.0;
   out_6472911724186297456[3] = 0.0;
   out_6472911724186297456[4] = 0.0;
   out_6472911724186297456[5] = 0.0;
   out_6472911724186297456[6] = 0.0;
   out_6472911724186297456[7] = 0.0;
   out_6472911724186297456[8] = 0.0;
   out_6472911724186297456[9] = 0.0;
   out_6472911724186297456[10] = 1.0;
   out_6472911724186297456[11] = 0.0;
   out_6472911724186297456[12] = 0.0;
   out_6472911724186297456[13] = 0.0;
   out_6472911724186297456[14] = 0.0;
   out_6472911724186297456[15] = 0.0;
   out_6472911724186297456[16] = 0.0;
   out_6472911724186297456[17] = 0.0;
   out_6472911724186297456[18] = 0.0;
   out_6472911724186297456[19] = 0.0;
   out_6472911724186297456[20] = 1.0;
   out_6472911724186297456[21] = 0.0;
   out_6472911724186297456[22] = 0.0;
   out_6472911724186297456[23] = 0.0;
   out_6472911724186297456[24] = 0.0;
   out_6472911724186297456[25] = 0.0;
   out_6472911724186297456[26] = 0.0;
   out_6472911724186297456[27] = 0.0;
   out_6472911724186297456[28] = 0.0;
   out_6472911724186297456[29] = 0.0;
   out_6472911724186297456[30] = 1.0;
   out_6472911724186297456[31] = 0.0;
   out_6472911724186297456[32] = 0.0;
   out_6472911724186297456[33] = 0.0;
   out_6472911724186297456[34] = 0.0;
   out_6472911724186297456[35] = 0.0;
   out_6472911724186297456[36] = 0.0;
   out_6472911724186297456[37] = 0.0;
   out_6472911724186297456[38] = 0.0;
   out_6472911724186297456[39] = 0.0;
   out_6472911724186297456[40] = 1.0;
   out_6472911724186297456[41] = 0.0;
   out_6472911724186297456[42] = 0.0;
   out_6472911724186297456[43] = 0.0;
   out_6472911724186297456[44] = 0.0;
   out_6472911724186297456[45] = 0.0;
   out_6472911724186297456[46] = 0.0;
   out_6472911724186297456[47] = 0.0;
   out_6472911724186297456[48] = 0.0;
   out_6472911724186297456[49] = 0.0;
   out_6472911724186297456[50] = 1.0;
   out_6472911724186297456[51] = 0.0;
   out_6472911724186297456[52] = 0.0;
   out_6472911724186297456[53] = 0.0;
   out_6472911724186297456[54] = 0.0;
   out_6472911724186297456[55] = 0.0;
   out_6472911724186297456[56] = 0.0;
   out_6472911724186297456[57] = 0.0;
   out_6472911724186297456[58] = 0.0;
   out_6472911724186297456[59] = 0.0;
   out_6472911724186297456[60] = 1.0;
   out_6472911724186297456[61] = 0.0;
   out_6472911724186297456[62] = 0.0;
   out_6472911724186297456[63] = 0.0;
   out_6472911724186297456[64] = 0.0;
   out_6472911724186297456[65] = 0.0;
   out_6472911724186297456[66] = 0.0;
   out_6472911724186297456[67] = 0.0;
   out_6472911724186297456[68] = 0.0;
   out_6472911724186297456[69] = 0.0;
   out_6472911724186297456[70] = 1.0;
   out_6472911724186297456[71] = 0.0;
   out_6472911724186297456[72] = 0.0;
   out_6472911724186297456[73] = 0.0;
   out_6472911724186297456[74] = 0.0;
   out_6472911724186297456[75] = 0.0;
   out_6472911724186297456[76] = 0.0;
   out_6472911724186297456[77] = 0.0;
   out_6472911724186297456[78] = 0.0;
   out_6472911724186297456[79] = 0.0;
   out_6472911724186297456[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_4383029369194465735) {
   out_4383029369194465735[0] = state[0];
   out_4383029369194465735[1] = state[1];
   out_4383029369194465735[2] = state[2];
   out_4383029369194465735[3] = state[3];
   out_4383029369194465735[4] = state[4];
   out_4383029369194465735[5] = dt*(stiffness_front*(-state[2] - state[3] + state[7])*state[0]/state[1] + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/state[4] + ((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4])*state[6] - 9.8100000000000005*state[8]) + state[5];
   out_4383029369194465735[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_4383029369194465735[7] = state[7];
   out_4383029369194465735[8] = state[8];
}
void F_fun(double *state, double dt, double *out_1598730726278697242) {
   out_1598730726278697242[0] = 1;
   out_1598730726278697242[1] = 0;
   out_1598730726278697242[2] = 0;
   out_1598730726278697242[3] = 0;
   out_1598730726278697242[4] = 0;
   out_1598730726278697242[5] = 0;
   out_1598730726278697242[6] = 0;
   out_1598730726278697242[7] = 0;
   out_1598730726278697242[8] = 0;
   out_1598730726278697242[9] = 0;
   out_1598730726278697242[10] = 1;
   out_1598730726278697242[11] = 0;
   out_1598730726278697242[12] = 0;
   out_1598730726278697242[13] = 0;
   out_1598730726278697242[14] = 0;
   out_1598730726278697242[15] = 0;
   out_1598730726278697242[16] = 0;
   out_1598730726278697242[17] = 0;
   out_1598730726278697242[18] = 0;
   out_1598730726278697242[19] = 0;
   out_1598730726278697242[20] = 1;
   out_1598730726278697242[21] = 0;
   out_1598730726278697242[22] = 0;
   out_1598730726278697242[23] = 0;
   out_1598730726278697242[24] = 0;
   out_1598730726278697242[25] = 0;
   out_1598730726278697242[26] = 0;
   out_1598730726278697242[27] = 0;
   out_1598730726278697242[28] = 0;
   out_1598730726278697242[29] = 0;
   out_1598730726278697242[30] = 1;
   out_1598730726278697242[31] = 0;
   out_1598730726278697242[32] = 0;
   out_1598730726278697242[33] = 0;
   out_1598730726278697242[34] = 0;
   out_1598730726278697242[35] = 0;
   out_1598730726278697242[36] = 0;
   out_1598730726278697242[37] = 0;
   out_1598730726278697242[38] = 0;
   out_1598730726278697242[39] = 0;
   out_1598730726278697242[40] = 1;
   out_1598730726278697242[41] = 0;
   out_1598730726278697242[42] = 0;
   out_1598730726278697242[43] = 0;
   out_1598730726278697242[44] = 0;
   out_1598730726278697242[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/state[1] + (-stiffness_front - stiffness_rear)*state[5]/state[4] + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/state[4]);
   out_1598730726278697242[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/pow(state[1], 2);
   out_1598730726278697242[47] = -dt*stiffness_front*state[0]/state[1];
   out_1598730726278697242[48] = -dt*stiffness_front*state[0]/state[1];
   out_1598730726278697242[49] = dt*(-(-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/pow(state[4], 2) + (-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/pow(state[4], 2) - 1)*state[6]);
   out_1598730726278697242[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/state[4] + 1;
   out_1598730726278697242[51] = dt*((-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/state[4] - state[4]);
   out_1598730726278697242[52] = dt*stiffness_front*state[0]/state[1];
   out_1598730726278697242[53] = -9.8100000000000005*dt;
   out_1598730726278697242[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_1598730726278697242[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_1598730726278697242[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1598730726278697242[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1598730726278697242[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_1598730726278697242[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_1598730726278697242[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_1598730726278697242[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_1598730726278697242[62] = 0;
   out_1598730726278697242[63] = 0;
   out_1598730726278697242[64] = 0;
   out_1598730726278697242[65] = 0;
   out_1598730726278697242[66] = 0;
   out_1598730726278697242[67] = 0;
   out_1598730726278697242[68] = 0;
   out_1598730726278697242[69] = 0;
   out_1598730726278697242[70] = 1;
   out_1598730726278697242[71] = 0;
   out_1598730726278697242[72] = 0;
   out_1598730726278697242[73] = 0;
   out_1598730726278697242[74] = 0;
   out_1598730726278697242[75] = 0;
   out_1598730726278697242[76] = 0;
   out_1598730726278697242[77] = 0;
   out_1598730726278697242[78] = 0;
   out_1598730726278697242[79] = 0;
   out_1598730726278697242[80] = 1;
}
void h_25(double *state, double *unused, double *out_6820208747041345332) {
   out_6820208747041345332[0] = state[6];
}
void H_25(double *state, double *unused, double *out_9109468649201723650) {
   out_9109468649201723650[0] = 0;
   out_9109468649201723650[1] = 0;
   out_9109468649201723650[2] = 0;
   out_9109468649201723650[3] = 0;
   out_9109468649201723650[4] = 0;
   out_9109468649201723650[5] = 0;
   out_9109468649201723650[6] = 1;
   out_9109468649201723650[7] = 0;
   out_9109468649201723650[8] = 0;
}
void h_24(double *state, double *unused, double *out_6116379550706621676) {
   out_6116379550706621676[0] = state[4];
   out_6116379550706621676[1] = state[5];
}
void H_24(double *state, double *unused, double *out_3298083018178946685) {
   out_3298083018178946685[0] = 0;
   out_3298083018178946685[1] = 0;
   out_3298083018178946685[2] = 0;
   out_3298083018178946685[3] = 0;
   out_3298083018178946685[4] = 1;
   out_3298083018178946685[5] = 0;
   out_3298083018178946685[6] = 0;
   out_3298083018178946685[7] = 0;
   out_3298083018178946685[8] = 0;
   out_3298083018178946685[9] = 0;
   out_3298083018178946685[10] = 0;
   out_3298083018178946685[11] = 0;
   out_3298083018178946685[12] = 0;
   out_3298083018178946685[13] = 0;
   out_3298083018178946685[14] = 1;
   out_3298083018178946685[15] = 0;
   out_3298083018178946685[16] = 0;
   out_3298083018178946685[17] = 0;
}
void h_30(double *state, double *unused, double *out_1061063903712703853) {
   out_1061063903712703853[0] = state[4];
}
void H_30(double *state, double *unused, double *out_9207936477364587896) {
   out_9207936477364587896[0] = 0;
   out_9207936477364587896[1] = 0;
   out_9207936477364587896[2] = 0;
   out_9207936477364587896[3] = 0;
   out_9207936477364587896[4] = 1;
   out_9207936477364587896[5] = 0;
   out_9207936477364587896[6] = 0;
   out_9207936477364587896[7] = 0;
   out_9207936477364587896[8] = 0;
}
void h_26(double *state, double *unused, double *out_3940609363948141792) {
   out_3940609363948141792[0] = state[7];
}
void H_26(double *state, double *unused, double *out_5595772105633771742) {
   out_5595772105633771742[0] = 0;
   out_5595772105633771742[1] = 0;
   out_5595772105633771742[2] = 0;
   out_5595772105633771742[3] = 0;
   out_5595772105633771742[4] = 0;
   out_5595772105633771742[5] = 0;
   out_5595772105633771742[6] = 0;
   out_5595772105633771742[7] = 1;
   out_5595772105633771742[8] = 0;
}
void h_27(double *state, double *unused, double *out_6216892862364867815) {
   out_6216892862364867815[0] = state[3];
}
void H_27(double *state, double *unused, double *out_7033173165564162985) {
   out_7033173165564162985[0] = 0;
   out_7033173165564162985[1] = 0;
   out_7033173165564162985[2] = 0;
   out_7033173165564162985[3] = 1;
   out_7033173165564162985[4] = 0;
   out_7033173165564162985[5] = 0;
   out_7033173165564162985[6] = 0;
   out_7033173165564162985[7] = 0;
   out_7033173165564162985[8] = 0;
}
void h_29(double *state, double *unused, double *out_2579443334110845465) {
   out_2579443334110845465[0] = state[1];
}
void H_29(double *state, double *unused, double *out_5319810438694611952) {
   out_5319810438694611952[0] = 0;
   out_5319810438694611952[1] = 1;
   out_5319810438694611952[2] = 0;
   out_5319810438694611952[3] = 0;
   out_5319810438694611952[4] = 0;
   out_5319810438694611952[5] = 0;
   out_5319810438694611952[6] = 0;
   out_5319810438694611952[7] = 0;
   out_5319810438694611952[8] = 0;
}
void h_28(double *state, double *unused, double *out_7160402715266530250) {
   out_7160402715266530250[0] = state[0];
}
void H_28(double *state, double *unused, double *out_7283440710259938203) {
   out_7283440710259938203[0] = 1;
   out_7283440710259938203[1] = 0;
   out_7283440710259938203[2] = 0;
   out_7283440710259938203[3] = 0;
   out_7283440710259938203[4] = 0;
   out_7283440710259938203[5] = 0;
   out_7283440710259938203[6] = 0;
   out_7283440710259938203[7] = 0;
   out_7283440710259938203[8] = 0;
}
void h_31(double *state, double *unused, double *out_8678809336312721323) {
   out_8678809336312721323[0] = state[8];
}
void H_31(double *state, double *unused, double *out_9078822687324763222) {
   out_9078822687324763222[0] = 0;
   out_9078822687324763222[1] = 0;
   out_9078822687324763222[2] = 0;
   out_9078822687324763222[3] = 0;
   out_9078822687324763222[4] = 0;
   out_9078822687324763222[5] = 0;
   out_9078822687324763222[6] = 0;
   out_9078822687324763222[7] = 0;
   out_9078822687324763222[8] = 1;
}
#include <eigen3/Eigen/Dense>
#include <iostream>

typedef Eigen::Matrix<double, DIM, DIM, Eigen::RowMajor> DDM;
typedef Eigen::Matrix<double, EDIM, EDIM, Eigen::RowMajor> EEM;
typedef Eigen::Matrix<double, DIM, EDIM, Eigen::RowMajor> DEM;

void predict(double *in_x, double *in_P, double *in_Q, double dt) {
  typedef Eigen::Matrix<double, MEDIM, MEDIM, Eigen::RowMajor> RRM;

  double nx[DIM] = {0};
  double in_F[EDIM*EDIM] = {0};

  // functions from sympy
  f_fun(in_x, dt, nx);
  F_fun(in_x, dt, in_F);


  EEM F(in_F);
  EEM P(in_P);
  EEM Q(in_Q);

  RRM F_main = F.topLeftCorner(MEDIM, MEDIM);
  P.topLeftCorner(MEDIM, MEDIM) = (F_main * P.topLeftCorner(MEDIM, MEDIM)) * F_main.transpose();
  P.topRightCorner(MEDIM, EDIM - MEDIM) = F_main * P.topRightCorner(MEDIM, EDIM - MEDIM);
  P.bottomLeftCorner(EDIM - MEDIM, MEDIM) = P.bottomLeftCorner(EDIM - MEDIM, MEDIM) * F_main.transpose();

  P = P + dt*Q;

  // copy out state
  memcpy(in_x, nx, DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
}

// note: extra_args dim only correct when null space projecting
// otherwise 1
template <int ZDIM, int EADIM, bool MAHA_TEST>
void update(double *in_x, double *in_P, Hfun h_fun, Hfun H_fun, Hfun Hea_fun, double *in_z, double *in_R, double *in_ea, double MAHA_THRESHOLD) {
  typedef Eigen::Matrix<double, ZDIM, ZDIM, Eigen::RowMajor> ZZM;
  typedef Eigen::Matrix<double, ZDIM, DIM, Eigen::RowMajor> ZDM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, EDIM, Eigen::RowMajor> XEM;
  //typedef Eigen::Matrix<double, EDIM, ZDIM, Eigen::RowMajor> EZM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, 1> X1M;
  typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> XXM;

  double in_hx[ZDIM] = {0};
  double in_H[ZDIM * DIM] = {0};
  double in_H_mod[EDIM * DIM] = {0};
  double delta_x[EDIM] = {0};
  double x_new[DIM] = {0};


  // state x, P
  Eigen::Matrix<double, ZDIM, 1> z(in_z);
  EEM P(in_P);
  ZZM pre_R(in_R);

  // functions from sympy
  h_fun(in_x, in_ea, in_hx);
  H_fun(in_x, in_ea, in_H);
  ZDM pre_H(in_H);

  // get y (y = z - hx)
  Eigen::Matrix<double, ZDIM, 1> pre_y(in_hx); pre_y = z - pre_y;
  X1M y; XXM H; XXM R;
  if (Hea_fun){
    typedef Eigen::Matrix<double, ZDIM, EADIM, Eigen::RowMajor> ZAM;
    double in_Hea[ZDIM * EADIM] = {0};
    Hea_fun(in_x, in_ea, in_Hea);
    ZAM Hea(in_Hea);
    XXM A = Hea.transpose().fullPivLu().kernel();


    y = A.transpose() * pre_y;
    H = A.transpose() * pre_H;
    R = A.transpose() * pre_R * A;
  } else {
    y = pre_y;
    H = pre_H;
    R = pre_R;
  }
  // get modified H
  H_mod_fun(in_x, in_H_mod);
  DEM H_mod(in_H_mod);
  XEM H_err = H * H_mod;

  // Do mahalobis distance test
  if (MAHA_TEST){
    XXM a = (H_err * P * H_err.transpose() + R).inverse();
    double maha_dist = y.transpose() * a * y;
    if (maha_dist > MAHA_THRESHOLD){
      R = 1.0e16 * R;
    }
  }

  // Outlier resilient weighting
  double weight = 1;//(1.5)/(1 + y.squaredNorm()/R.sum());

  // kalman gains and I_KH
  XXM S = ((H_err * P) * H_err.transpose()) + R/weight;
  XEM KT = S.fullPivLu().solve(H_err * P.transpose());
  //EZM K = KT.transpose(); TODO: WHY DOES THIS NOT COMPILE?
  //EZM K = S.fullPivLu().solve(H_err * P.transpose()).transpose();
  //std::cout << "Here is the matrix rot:\n" << K << std::endl;
  EEM I_KH = Eigen::Matrix<double, EDIM, EDIM>::Identity() - (KT.transpose() * H_err);

  // update state by injecting dx
  Eigen::Matrix<double, EDIM, 1> dx(delta_x);
  dx  = (KT.transpose() * y);
  memcpy(delta_x, dx.data(), EDIM * sizeof(double));
  err_fun(in_x, delta_x, x_new);
  Eigen::Matrix<double, DIM, 1> x(x_new);

  // update cov
  P = ((I_KH * P) * I_KH.transpose()) + ((KT.transpose() * R) * KT);

  // copy out state
  memcpy(in_x, x.data(), DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
  memcpy(in_z, y.data(), y.rows() * sizeof(double));
}




}
extern "C" {

void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_25, H_25, NULL, in_z, in_R, in_ea, MAHA_THRESH_25);
}
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<2, 3, 0>(in_x, in_P, h_24, H_24, NULL, in_z, in_R, in_ea, MAHA_THRESH_24);
}
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_30, H_30, NULL, in_z, in_R, in_ea, MAHA_THRESH_30);
}
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_26, H_26, NULL, in_z, in_R, in_ea, MAHA_THRESH_26);
}
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_27, H_27, NULL, in_z, in_R, in_ea, MAHA_THRESH_27);
}
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_29, H_29, NULL, in_z, in_R, in_ea, MAHA_THRESH_29);
}
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_28, H_28, NULL, in_z, in_R, in_ea, MAHA_THRESH_28);
}
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_31, H_31, NULL, in_z, in_R, in_ea, MAHA_THRESH_31);
}
void car_err_fun(double *nom_x, double *delta_x, double *out_351073186439356103) {
  err_fun(nom_x, delta_x, out_351073186439356103);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1747083980238712734) {
  inv_err_fun(nom_x, true_x, out_1747083980238712734);
}
void car_H_mod_fun(double *state, double *out_6472911724186297456) {
  H_mod_fun(state, out_6472911724186297456);
}
void car_f_fun(double *state, double dt, double *out_4383029369194465735) {
  f_fun(state,  dt, out_4383029369194465735);
}
void car_F_fun(double *state, double dt, double *out_1598730726278697242) {
  F_fun(state,  dt, out_1598730726278697242);
}
void car_h_25(double *state, double *unused, double *out_6820208747041345332) {
  h_25(state, unused, out_6820208747041345332);
}
void car_H_25(double *state, double *unused, double *out_9109468649201723650) {
  H_25(state, unused, out_9109468649201723650);
}
void car_h_24(double *state, double *unused, double *out_6116379550706621676) {
  h_24(state, unused, out_6116379550706621676);
}
void car_H_24(double *state, double *unused, double *out_3298083018178946685) {
  H_24(state, unused, out_3298083018178946685);
}
void car_h_30(double *state, double *unused, double *out_1061063903712703853) {
  h_30(state, unused, out_1061063903712703853);
}
void car_H_30(double *state, double *unused, double *out_9207936477364587896) {
  H_30(state, unused, out_9207936477364587896);
}
void car_h_26(double *state, double *unused, double *out_3940609363948141792) {
  h_26(state, unused, out_3940609363948141792);
}
void car_H_26(double *state, double *unused, double *out_5595772105633771742) {
  H_26(state, unused, out_5595772105633771742);
}
void car_h_27(double *state, double *unused, double *out_6216892862364867815) {
  h_27(state, unused, out_6216892862364867815);
}
void car_H_27(double *state, double *unused, double *out_7033173165564162985) {
  H_27(state, unused, out_7033173165564162985);
}
void car_h_29(double *state, double *unused, double *out_2579443334110845465) {
  h_29(state, unused, out_2579443334110845465);
}
void car_H_29(double *state, double *unused, double *out_5319810438694611952) {
  H_29(state, unused, out_5319810438694611952);
}
void car_h_28(double *state, double *unused, double *out_7160402715266530250) {
  h_28(state, unused, out_7160402715266530250);
}
void car_H_28(double *state, double *unused, double *out_7283440710259938203) {
  H_28(state, unused, out_7283440710259938203);
}
void car_h_31(double *state, double *unused, double *out_8678809336312721323) {
  h_31(state, unused, out_8678809336312721323);
}
void car_H_31(double *state, double *unused, double *out_9078822687324763222) {
  H_31(state, unused, out_9078822687324763222);
}
void car_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
void car_set_rotational_inertia(double x) {
  set_rotational_inertia(x);
}
void car_set_center_to_front(double x) {
  set_center_to_front(x);
}
void car_set_center_to_rear(double x) {
  set_center_to_rear(x);
}
void car_set_stiffness_front(double x) {
  set_stiffness_front(x);
}
void car_set_stiffness_rear(double x) {
  set_stiffness_rear(x);
}
}

const EKF car = {
  .name = "car",
  .kinds = { 25, 24, 30, 26, 27, 29, 28, 31 },
  .feature_kinds = {  },
  .f_fun = car_f_fun,
  .F_fun = car_F_fun,
  .err_fun = car_err_fun,
  .inv_err_fun = car_inv_err_fun,
  .H_mod_fun = car_H_mod_fun,
  .predict = car_predict,
  .hs = {
    { 25, car_h_25 },
    { 24, car_h_24 },
    { 30, car_h_30 },
    { 26, car_h_26 },
    { 27, car_h_27 },
    { 29, car_h_29 },
    { 28, car_h_28 },
    { 31, car_h_31 },
  },
  .Hs = {
    { 25, car_H_25 },
    { 24, car_H_24 },
    { 30, car_H_30 },
    { 26, car_H_26 },
    { 27, car_H_27 },
    { 29, car_H_29 },
    { 28, car_H_28 },
    { 31, car_H_31 },
  },
  .updates = {
    { 25, car_update_25 },
    { 24, car_update_24 },
    { 30, car_update_30 },
    { 26, car_update_26 },
    { 27, car_update_27 },
    { 29, car_update_29 },
    { 28, car_update_28 },
    { 31, car_update_31 },
  },
  .Hes = {
  },
  .sets = {
    { "rotational_inertia", car_set_rotational_inertia },
    { "center_to_front", car_set_center_to_front },
    { "center_to_rear", car_set_center_to_rear },
    { "stiffness_front", car_set_stiffness_front },
    { "stiffness_rear", car_set_stiffness_rear },
  },
  .extra_routines = {
  },
};

ekf_lib_init(car)
