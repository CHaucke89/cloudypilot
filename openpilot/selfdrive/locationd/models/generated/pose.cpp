#include "pose.h"

namespace {
#define DIM 18
#define EDIM 18
#define MEDIM 18
typedef void (*Hfun)(double *, double *, double *);
const static double MAHA_THRESH_4 = 7.814727903251177;
const static double MAHA_THRESH_10 = 7.814727903251177;
const static double MAHA_THRESH_13 = 7.814727903251177;
const static double MAHA_THRESH_14 = 7.814727903251177;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_5456529213378525094) {
   out_5456529213378525094[0] = delta_x[0] + nom_x[0];
   out_5456529213378525094[1] = delta_x[1] + nom_x[1];
   out_5456529213378525094[2] = delta_x[2] + nom_x[2];
   out_5456529213378525094[3] = delta_x[3] + nom_x[3];
   out_5456529213378525094[4] = delta_x[4] + nom_x[4];
   out_5456529213378525094[5] = delta_x[5] + nom_x[5];
   out_5456529213378525094[6] = delta_x[6] + nom_x[6];
   out_5456529213378525094[7] = delta_x[7] + nom_x[7];
   out_5456529213378525094[8] = delta_x[8] + nom_x[8];
   out_5456529213378525094[9] = delta_x[9] + nom_x[9];
   out_5456529213378525094[10] = delta_x[10] + nom_x[10];
   out_5456529213378525094[11] = delta_x[11] + nom_x[11];
   out_5456529213378525094[12] = delta_x[12] + nom_x[12];
   out_5456529213378525094[13] = delta_x[13] + nom_x[13];
   out_5456529213378525094[14] = delta_x[14] + nom_x[14];
   out_5456529213378525094[15] = delta_x[15] + nom_x[15];
   out_5456529213378525094[16] = delta_x[16] + nom_x[16];
   out_5456529213378525094[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5389676744893681967) {
   out_5389676744893681967[0] = -nom_x[0] + true_x[0];
   out_5389676744893681967[1] = -nom_x[1] + true_x[1];
   out_5389676744893681967[2] = -nom_x[2] + true_x[2];
   out_5389676744893681967[3] = -nom_x[3] + true_x[3];
   out_5389676744893681967[4] = -nom_x[4] + true_x[4];
   out_5389676744893681967[5] = -nom_x[5] + true_x[5];
   out_5389676744893681967[6] = -nom_x[6] + true_x[6];
   out_5389676744893681967[7] = -nom_x[7] + true_x[7];
   out_5389676744893681967[8] = -nom_x[8] + true_x[8];
   out_5389676744893681967[9] = -nom_x[9] + true_x[9];
   out_5389676744893681967[10] = -nom_x[10] + true_x[10];
   out_5389676744893681967[11] = -nom_x[11] + true_x[11];
   out_5389676744893681967[12] = -nom_x[12] + true_x[12];
   out_5389676744893681967[13] = -nom_x[13] + true_x[13];
   out_5389676744893681967[14] = -nom_x[14] + true_x[14];
   out_5389676744893681967[15] = -nom_x[15] + true_x[15];
   out_5389676744893681967[16] = -nom_x[16] + true_x[16];
   out_5389676744893681967[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_6025654641358348591) {
   out_6025654641358348591[0] = 1.0;
   out_6025654641358348591[1] = 0.0;
   out_6025654641358348591[2] = 0.0;
   out_6025654641358348591[3] = 0.0;
   out_6025654641358348591[4] = 0.0;
   out_6025654641358348591[5] = 0.0;
   out_6025654641358348591[6] = 0.0;
   out_6025654641358348591[7] = 0.0;
   out_6025654641358348591[8] = 0.0;
   out_6025654641358348591[9] = 0.0;
   out_6025654641358348591[10] = 0.0;
   out_6025654641358348591[11] = 0.0;
   out_6025654641358348591[12] = 0.0;
   out_6025654641358348591[13] = 0.0;
   out_6025654641358348591[14] = 0.0;
   out_6025654641358348591[15] = 0.0;
   out_6025654641358348591[16] = 0.0;
   out_6025654641358348591[17] = 0.0;
   out_6025654641358348591[18] = 0.0;
   out_6025654641358348591[19] = 1.0;
   out_6025654641358348591[20] = 0.0;
   out_6025654641358348591[21] = 0.0;
   out_6025654641358348591[22] = 0.0;
   out_6025654641358348591[23] = 0.0;
   out_6025654641358348591[24] = 0.0;
   out_6025654641358348591[25] = 0.0;
   out_6025654641358348591[26] = 0.0;
   out_6025654641358348591[27] = 0.0;
   out_6025654641358348591[28] = 0.0;
   out_6025654641358348591[29] = 0.0;
   out_6025654641358348591[30] = 0.0;
   out_6025654641358348591[31] = 0.0;
   out_6025654641358348591[32] = 0.0;
   out_6025654641358348591[33] = 0.0;
   out_6025654641358348591[34] = 0.0;
   out_6025654641358348591[35] = 0.0;
   out_6025654641358348591[36] = 0.0;
   out_6025654641358348591[37] = 0.0;
   out_6025654641358348591[38] = 1.0;
   out_6025654641358348591[39] = 0.0;
   out_6025654641358348591[40] = 0.0;
   out_6025654641358348591[41] = 0.0;
   out_6025654641358348591[42] = 0.0;
   out_6025654641358348591[43] = 0.0;
   out_6025654641358348591[44] = 0.0;
   out_6025654641358348591[45] = 0.0;
   out_6025654641358348591[46] = 0.0;
   out_6025654641358348591[47] = 0.0;
   out_6025654641358348591[48] = 0.0;
   out_6025654641358348591[49] = 0.0;
   out_6025654641358348591[50] = 0.0;
   out_6025654641358348591[51] = 0.0;
   out_6025654641358348591[52] = 0.0;
   out_6025654641358348591[53] = 0.0;
   out_6025654641358348591[54] = 0.0;
   out_6025654641358348591[55] = 0.0;
   out_6025654641358348591[56] = 0.0;
   out_6025654641358348591[57] = 1.0;
   out_6025654641358348591[58] = 0.0;
   out_6025654641358348591[59] = 0.0;
   out_6025654641358348591[60] = 0.0;
   out_6025654641358348591[61] = 0.0;
   out_6025654641358348591[62] = 0.0;
   out_6025654641358348591[63] = 0.0;
   out_6025654641358348591[64] = 0.0;
   out_6025654641358348591[65] = 0.0;
   out_6025654641358348591[66] = 0.0;
   out_6025654641358348591[67] = 0.0;
   out_6025654641358348591[68] = 0.0;
   out_6025654641358348591[69] = 0.0;
   out_6025654641358348591[70] = 0.0;
   out_6025654641358348591[71] = 0.0;
   out_6025654641358348591[72] = 0.0;
   out_6025654641358348591[73] = 0.0;
   out_6025654641358348591[74] = 0.0;
   out_6025654641358348591[75] = 0.0;
   out_6025654641358348591[76] = 1.0;
   out_6025654641358348591[77] = 0.0;
   out_6025654641358348591[78] = 0.0;
   out_6025654641358348591[79] = 0.0;
   out_6025654641358348591[80] = 0.0;
   out_6025654641358348591[81] = 0.0;
   out_6025654641358348591[82] = 0.0;
   out_6025654641358348591[83] = 0.0;
   out_6025654641358348591[84] = 0.0;
   out_6025654641358348591[85] = 0.0;
   out_6025654641358348591[86] = 0.0;
   out_6025654641358348591[87] = 0.0;
   out_6025654641358348591[88] = 0.0;
   out_6025654641358348591[89] = 0.0;
   out_6025654641358348591[90] = 0.0;
   out_6025654641358348591[91] = 0.0;
   out_6025654641358348591[92] = 0.0;
   out_6025654641358348591[93] = 0.0;
   out_6025654641358348591[94] = 0.0;
   out_6025654641358348591[95] = 1.0;
   out_6025654641358348591[96] = 0.0;
   out_6025654641358348591[97] = 0.0;
   out_6025654641358348591[98] = 0.0;
   out_6025654641358348591[99] = 0.0;
   out_6025654641358348591[100] = 0.0;
   out_6025654641358348591[101] = 0.0;
   out_6025654641358348591[102] = 0.0;
   out_6025654641358348591[103] = 0.0;
   out_6025654641358348591[104] = 0.0;
   out_6025654641358348591[105] = 0.0;
   out_6025654641358348591[106] = 0.0;
   out_6025654641358348591[107] = 0.0;
   out_6025654641358348591[108] = 0.0;
   out_6025654641358348591[109] = 0.0;
   out_6025654641358348591[110] = 0.0;
   out_6025654641358348591[111] = 0.0;
   out_6025654641358348591[112] = 0.0;
   out_6025654641358348591[113] = 0.0;
   out_6025654641358348591[114] = 1.0;
   out_6025654641358348591[115] = 0.0;
   out_6025654641358348591[116] = 0.0;
   out_6025654641358348591[117] = 0.0;
   out_6025654641358348591[118] = 0.0;
   out_6025654641358348591[119] = 0.0;
   out_6025654641358348591[120] = 0.0;
   out_6025654641358348591[121] = 0.0;
   out_6025654641358348591[122] = 0.0;
   out_6025654641358348591[123] = 0.0;
   out_6025654641358348591[124] = 0.0;
   out_6025654641358348591[125] = 0.0;
   out_6025654641358348591[126] = 0.0;
   out_6025654641358348591[127] = 0.0;
   out_6025654641358348591[128] = 0.0;
   out_6025654641358348591[129] = 0.0;
   out_6025654641358348591[130] = 0.0;
   out_6025654641358348591[131] = 0.0;
   out_6025654641358348591[132] = 0.0;
   out_6025654641358348591[133] = 1.0;
   out_6025654641358348591[134] = 0.0;
   out_6025654641358348591[135] = 0.0;
   out_6025654641358348591[136] = 0.0;
   out_6025654641358348591[137] = 0.0;
   out_6025654641358348591[138] = 0.0;
   out_6025654641358348591[139] = 0.0;
   out_6025654641358348591[140] = 0.0;
   out_6025654641358348591[141] = 0.0;
   out_6025654641358348591[142] = 0.0;
   out_6025654641358348591[143] = 0.0;
   out_6025654641358348591[144] = 0.0;
   out_6025654641358348591[145] = 0.0;
   out_6025654641358348591[146] = 0.0;
   out_6025654641358348591[147] = 0.0;
   out_6025654641358348591[148] = 0.0;
   out_6025654641358348591[149] = 0.0;
   out_6025654641358348591[150] = 0.0;
   out_6025654641358348591[151] = 0.0;
   out_6025654641358348591[152] = 1.0;
   out_6025654641358348591[153] = 0.0;
   out_6025654641358348591[154] = 0.0;
   out_6025654641358348591[155] = 0.0;
   out_6025654641358348591[156] = 0.0;
   out_6025654641358348591[157] = 0.0;
   out_6025654641358348591[158] = 0.0;
   out_6025654641358348591[159] = 0.0;
   out_6025654641358348591[160] = 0.0;
   out_6025654641358348591[161] = 0.0;
   out_6025654641358348591[162] = 0.0;
   out_6025654641358348591[163] = 0.0;
   out_6025654641358348591[164] = 0.0;
   out_6025654641358348591[165] = 0.0;
   out_6025654641358348591[166] = 0.0;
   out_6025654641358348591[167] = 0.0;
   out_6025654641358348591[168] = 0.0;
   out_6025654641358348591[169] = 0.0;
   out_6025654641358348591[170] = 0.0;
   out_6025654641358348591[171] = 1.0;
   out_6025654641358348591[172] = 0.0;
   out_6025654641358348591[173] = 0.0;
   out_6025654641358348591[174] = 0.0;
   out_6025654641358348591[175] = 0.0;
   out_6025654641358348591[176] = 0.0;
   out_6025654641358348591[177] = 0.0;
   out_6025654641358348591[178] = 0.0;
   out_6025654641358348591[179] = 0.0;
   out_6025654641358348591[180] = 0.0;
   out_6025654641358348591[181] = 0.0;
   out_6025654641358348591[182] = 0.0;
   out_6025654641358348591[183] = 0.0;
   out_6025654641358348591[184] = 0.0;
   out_6025654641358348591[185] = 0.0;
   out_6025654641358348591[186] = 0.0;
   out_6025654641358348591[187] = 0.0;
   out_6025654641358348591[188] = 0.0;
   out_6025654641358348591[189] = 0.0;
   out_6025654641358348591[190] = 1.0;
   out_6025654641358348591[191] = 0.0;
   out_6025654641358348591[192] = 0.0;
   out_6025654641358348591[193] = 0.0;
   out_6025654641358348591[194] = 0.0;
   out_6025654641358348591[195] = 0.0;
   out_6025654641358348591[196] = 0.0;
   out_6025654641358348591[197] = 0.0;
   out_6025654641358348591[198] = 0.0;
   out_6025654641358348591[199] = 0.0;
   out_6025654641358348591[200] = 0.0;
   out_6025654641358348591[201] = 0.0;
   out_6025654641358348591[202] = 0.0;
   out_6025654641358348591[203] = 0.0;
   out_6025654641358348591[204] = 0.0;
   out_6025654641358348591[205] = 0.0;
   out_6025654641358348591[206] = 0.0;
   out_6025654641358348591[207] = 0.0;
   out_6025654641358348591[208] = 0.0;
   out_6025654641358348591[209] = 1.0;
   out_6025654641358348591[210] = 0.0;
   out_6025654641358348591[211] = 0.0;
   out_6025654641358348591[212] = 0.0;
   out_6025654641358348591[213] = 0.0;
   out_6025654641358348591[214] = 0.0;
   out_6025654641358348591[215] = 0.0;
   out_6025654641358348591[216] = 0.0;
   out_6025654641358348591[217] = 0.0;
   out_6025654641358348591[218] = 0.0;
   out_6025654641358348591[219] = 0.0;
   out_6025654641358348591[220] = 0.0;
   out_6025654641358348591[221] = 0.0;
   out_6025654641358348591[222] = 0.0;
   out_6025654641358348591[223] = 0.0;
   out_6025654641358348591[224] = 0.0;
   out_6025654641358348591[225] = 0.0;
   out_6025654641358348591[226] = 0.0;
   out_6025654641358348591[227] = 0.0;
   out_6025654641358348591[228] = 1.0;
   out_6025654641358348591[229] = 0.0;
   out_6025654641358348591[230] = 0.0;
   out_6025654641358348591[231] = 0.0;
   out_6025654641358348591[232] = 0.0;
   out_6025654641358348591[233] = 0.0;
   out_6025654641358348591[234] = 0.0;
   out_6025654641358348591[235] = 0.0;
   out_6025654641358348591[236] = 0.0;
   out_6025654641358348591[237] = 0.0;
   out_6025654641358348591[238] = 0.0;
   out_6025654641358348591[239] = 0.0;
   out_6025654641358348591[240] = 0.0;
   out_6025654641358348591[241] = 0.0;
   out_6025654641358348591[242] = 0.0;
   out_6025654641358348591[243] = 0.0;
   out_6025654641358348591[244] = 0.0;
   out_6025654641358348591[245] = 0.0;
   out_6025654641358348591[246] = 0.0;
   out_6025654641358348591[247] = 1.0;
   out_6025654641358348591[248] = 0.0;
   out_6025654641358348591[249] = 0.0;
   out_6025654641358348591[250] = 0.0;
   out_6025654641358348591[251] = 0.0;
   out_6025654641358348591[252] = 0.0;
   out_6025654641358348591[253] = 0.0;
   out_6025654641358348591[254] = 0.0;
   out_6025654641358348591[255] = 0.0;
   out_6025654641358348591[256] = 0.0;
   out_6025654641358348591[257] = 0.0;
   out_6025654641358348591[258] = 0.0;
   out_6025654641358348591[259] = 0.0;
   out_6025654641358348591[260] = 0.0;
   out_6025654641358348591[261] = 0.0;
   out_6025654641358348591[262] = 0.0;
   out_6025654641358348591[263] = 0.0;
   out_6025654641358348591[264] = 0.0;
   out_6025654641358348591[265] = 0.0;
   out_6025654641358348591[266] = 1.0;
   out_6025654641358348591[267] = 0.0;
   out_6025654641358348591[268] = 0.0;
   out_6025654641358348591[269] = 0.0;
   out_6025654641358348591[270] = 0.0;
   out_6025654641358348591[271] = 0.0;
   out_6025654641358348591[272] = 0.0;
   out_6025654641358348591[273] = 0.0;
   out_6025654641358348591[274] = 0.0;
   out_6025654641358348591[275] = 0.0;
   out_6025654641358348591[276] = 0.0;
   out_6025654641358348591[277] = 0.0;
   out_6025654641358348591[278] = 0.0;
   out_6025654641358348591[279] = 0.0;
   out_6025654641358348591[280] = 0.0;
   out_6025654641358348591[281] = 0.0;
   out_6025654641358348591[282] = 0.0;
   out_6025654641358348591[283] = 0.0;
   out_6025654641358348591[284] = 0.0;
   out_6025654641358348591[285] = 1.0;
   out_6025654641358348591[286] = 0.0;
   out_6025654641358348591[287] = 0.0;
   out_6025654641358348591[288] = 0.0;
   out_6025654641358348591[289] = 0.0;
   out_6025654641358348591[290] = 0.0;
   out_6025654641358348591[291] = 0.0;
   out_6025654641358348591[292] = 0.0;
   out_6025654641358348591[293] = 0.0;
   out_6025654641358348591[294] = 0.0;
   out_6025654641358348591[295] = 0.0;
   out_6025654641358348591[296] = 0.0;
   out_6025654641358348591[297] = 0.0;
   out_6025654641358348591[298] = 0.0;
   out_6025654641358348591[299] = 0.0;
   out_6025654641358348591[300] = 0.0;
   out_6025654641358348591[301] = 0.0;
   out_6025654641358348591[302] = 0.0;
   out_6025654641358348591[303] = 0.0;
   out_6025654641358348591[304] = 1.0;
   out_6025654641358348591[305] = 0.0;
   out_6025654641358348591[306] = 0.0;
   out_6025654641358348591[307] = 0.0;
   out_6025654641358348591[308] = 0.0;
   out_6025654641358348591[309] = 0.0;
   out_6025654641358348591[310] = 0.0;
   out_6025654641358348591[311] = 0.0;
   out_6025654641358348591[312] = 0.0;
   out_6025654641358348591[313] = 0.0;
   out_6025654641358348591[314] = 0.0;
   out_6025654641358348591[315] = 0.0;
   out_6025654641358348591[316] = 0.0;
   out_6025654641358348591[317] = 0.0;
   out_6025654641358348591[318] = 0.0;
   out_6025654641358348591[319] = 0.0;
   out_6025654641358348591[320] = 0.0;
   out_6025654641358348591[321] = 0.0;
   out_6025654641358348591[322] = 0.0;
   out_6025654641358348591[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_8477885110547017436) {
   out_8477885110547017436[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_8477885110547017436[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_8477885110547017436[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_8477885110547017436[3] = dt*state[12] + state[3];
   out_8477885110547017436[4] = dt*state[13] + state[4];
   out_8477885110547017436[5] = dt*state[14] + state[5];
   out_8477885110547017436[6] = state[6];
   out_8477885110547017436[7] = state[7];
   out_8477885110547017436[8] = state[8];
   out_8477885110547017436[9] = state[9];
   out_8477885110547017436[10] = state[10];
   out_8477885110547017436[11] = state[11];
   out_8477885110547017436[12] = state[12];
   out_8477885110547017436[13] = state[13];
   out_8477885110547017436[14] = state[14];
   out_8477885110547017436[15] = state[15];
   out_8477885110547017436[16] = state[16];
   out_8477885110547017436[17] = state[17];
}
void F_fun(double *state, double dt, double *out_4130905704562196471) {
   out_4130905704562196471[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4130905704562196471[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4130905704562196471[2] = 0;
   out_4130905704562196471[3] = 0;
   out_4130905704562196471[4] = 0;
   out_4130905704562196471[5] = 0;
   out_4130905704562196471[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4130905704562196471[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4130905704562196471[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4130905704562196471[9] = 0;
   out_4130905704562196471[10] = 0;
   out_4130905704562196471[11] = 0;
   out_4130905704562196471[12] = 0;
   out_4130905704562196471[13] = 0;
   out_4130905704562196471[14] = 0;
   out_4130905704562196471[15] = 0;
   out_4130905704562196471[16] = 0;
   out_4130905704562196471[17] = 0;
   out_4130905704562196471[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4130905704562196471[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4130905704562196471[20] = 0;
   out_4130905704562196471[21] = 0;
   out_4130905704562196471[22] = 0;
   out_4130905704562196471[23] = 0;
   out_4130905704562196471[24] = 0;
   out_4130905704562196471[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4130905704562196471[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4130905704562196471[27] = 0;
   out_4130905704562196471[28] = 0;
   out_4130905704562196471[29] = 0;
   out_4130905704562196471[30] = 0;
   out_4130905704562196471[31] = 0;
   out_4130905704562196471[32] = 0;
   out_4130905704562196471[33] = 0;
   out_4130905704562196471[34] = 0;
   out_4130905704562196471[35] = 0;
   out_4130905704562196471[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4130905704562196471[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4130905704562196471[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4130905704562196471[39] = 0;
   out_4130905704562196471[40] = 0;
   out_4130905704562196471[41] = 0;
   out_4130905704562196471[42] = 0;
   out_4130905704562196471[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4130905704562196471[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4130905704562196471[45] = 0;
   out_4130905704562196471[46] = 0;
   out_4130905704562196471[47] = 0;
   out_4130905704562196471[48] = 0;
   out_4130905704562196471[49] = 0;
   out_4130905704562196471[50] = 0;
   out_4130905704562196471[51] = 0;
   out_4130905704562196471[52] = 0;
   out_4130905704562196471[53] = 0;
   out_4130905704562196471[54] = 0;
   out_4130905704562196471[55] = 0;
   out_4130905704562196471[56] = 0;
   out_4130905704562196471[57] = 1;
   out_4130905704562196471[58] = 0;
   out_4130905704562196471[59] = 0;
   out_4130905704562196471[60] = 0;
   out_4130905704562196471[61] = 0;
   out_4130905704562196471[62] = 0;
   out_4130905704562196471[63] = 0;
   out_4130905704562196471[64] = 0;
   out_4130905704562196471[65] = 0;
   out_4130905704562196471[66] = dt;
   out_4130905704562196471[67] = 0;
   out_4130905704562196471[68] = 0;
   out_4130905704562196471[69] = 0;
   out_4130905704562196471[70] = 0;
   out_4130905704562196471[71] = 0;
   out_4130905704562196471[72] = 0;
   out_4130905704562196471[73] = 0;
   out_4130905704562196471[74] = 0;
   out_4130905704562196471[75] = 0;
   out_4130905704562196471[76] = 1;
   out_4130905704562196471[77] = 0;
   out_4130905704562196471[78] = 0;
   out_4130905704562196471[79] = 0;
   out_4130905704562196471[80] = 0;
   out_4130905704562196471[81] = 0;
   out_4130905704562196471[82] = 0;
   out_4130905704562196471[83] = 0;
   out_4130905704562196471[84] = 0;
   out_4130905704562196471[85] = dt;
   out_4130905704562196471[86] = 0;
   out_4130905704562196471[87] = 0;
   out_4130905704562196471[88] = 0;
   out_4130905704562196471[89] = 0;
   out_4130905704562196471[90] = 0;
   out_4130905704562196471[91] = 0;
   out_4130905704562196471[92] = 0;
   out_4130905704562196471[93] = 0;
   out_4130905704562196471[94] = 0;
   out_4130905704562196471[95] = 1;
   out_4130905704562196471[96] = 0;
   out_4130905704562196471[97] = 0;
   out_4130905704562196471[98] = 0;
   out_4130905704562196471[99] = 0;
   out_4130905704562196471[100] = 0;
   out_4130905704562196471[101] = 0;
   out_4130905704562196471[102] = 0;
   out_4130905704562196471[103] = 0;
   out_4130905704562196471[104] = dt;
   out_4130905704562196471[105] = 0;
   out_4130905704562196471[106] = 0;
   out_4130905704562196471[107] = 0;
   out_4130905704562196471[108] = 0;
   out_4130905704562196471[109] = 0;
   out_4130905704562196471[110] = 0;
   out_4130905704562196471[111] = 0;
   out_4130905704562196471[112] = 0;
   out_4130905704562196471[113] = 0;
   out_4130905704562196471[114] = 1;
   out_4130905704562196471[115] = 0;
   out_4130905704562196471[116] = 0;
   out_4130905704562196471[117] = 0;
   out_4130905704562196471[118] = 0;
   out_4130905704562196471[119] = 0;
   out_4130905704562196471[120] = 0;
   out_4130905704562196471[121] = 0;
   out_4130905704562196471[122] = 0;
   out_4130905704562196471[123] = 0;
   out_4130905704562196471[124] = 0;
   out_4130905704562196471[125] = 0;
   out_4130905704562196471[126] = 0;
   out_4130905704562196471[127] = 0;
   out_4130905704562196471[128] = 0;
   out_4130905704562196471[129] = 0;
   out_4130905704562196471[130] = 0;
   out_4130905704562196471[131] = 0;
   out_4130905704562196471[132] = 0;
   out_4130905704562196471[133] = 1;
   out_4130905704562196471[134] = 0;
   out_4130905704562196471[135] = 0;
   out_4130905704562196471[136] = 0;
   out_4130905704562196471[137] = 0;
   out_4130905704562196471[138] = 0;
   out_4130905704562196471[139] = 0;
   out_4130905704562196471[140] = 0;
   out_4130905704562196471[141] = 0;
   out_4130905704562196471[142] = 0;
   out_4130905704562196471[143] = 0;
   out_4130905704562196471[144] = 0;
   out_4130905704562196471[145] = 0;
   out_4130905704562196471[146] = 0;
   out_4130905704562196471[147] = 0;
   out_4130905704562196471[148] = 0;
   out_4130905704562196471[149] = 0;
   out_4130905704562196471[150] = 0;
   out_4130905704562196471[151] = 0;
   out_4130905704562196471[152] = 1;
   out_4130905704562196471[153] = 0;
   out_4130905704562196471[154] = 0;
   out_4130905704562196471[155] = 0;
   out_4130905704562196471[156] = 0;
   out_4130905704562196471[157] = 0;
   out_4130905704562196471[158] = 0;
   out_4130905704562196471[159] = 0;
   out_4130905704562196471[160] = 0;
   out_4130905704562196471[161] = 0;
   out_4130905704562196471[162] = 0;
   out_4130905704562196471[163] = 0;
   out_4130905704562196471[164] = 0;
   out_4130905704562196471[165] = 0;
   out_4130905704562196471[166] = 0;
   out_4130905704562196471[167] = 0;
   out_4130905704562196471[168] = 0;
   out_4130905704562196471[169] = 0;
   out_4130905704562196471[170] = 0;
   out_4130905704562196471[171] = 1;
   out_4130905704562196471[172] = 0;
   out_4130905704562196471[173] = 0;
   out_4130905704562196471[174] = 0;
   out_4130905704562196471[175] = 0;
   out_4130905704562196471[176] = 0;
   out_4130905704562196471[177] = 0;
   out_4130905704562196471[178] = 0;
   out_4130905704562196471[179] = 0;
   out_4130905704562196471[180] = 0;
   out_4130905704562196471[181] = 0;
   out_4130905704562196471[182] = 0;
   out_4130905704562196471[183] = 0;
   out_4130905704562196471[184] = 0;
   out_4130905704562196471[185] = 0;
   out_4130905704562196471[186] = 0;
   out_4130905704562196471[187] = 0;
   out_4130905704562196471[188] = 0;
   out_4130905704562196471[189] = 0;
   out_4130905704562196471[190] = 1;
   out_4130905704562196471[191] = 0;
   out_4130905704562196471[192] = 0;
   out_4130905704562196471[193] = 0;
   out_4130905704562196471[194] = 0;
   out_4130905704562196471[195] = 0;
   out_4130905704562196471[196] = 0;
   out_4130905704562196471[197] = 0;
   out_4130905704562196471[198] = 0;
   out_4130905704562196471[199] = 0;
   out_4130905704562196471[200] = 0;
   out_4130905704562196471[201] = 0;
   out_4130905704562196471[202] = 0;
   out_4130905704562196471[203] = 0;
   out_4130905704562196471[204] = 0;
   out_4130905704562196471[205] = 0;
   out_4130905704562196471[206] = 0;
   out_4130905704562196471[207] = 0;
   out_4130905704562196471[208] = 0;
   out_4130905704562196471[209] = 1;
   out_4130905704562196471[210] = 0;
   out_4130905704562196471[211] = 0;
   out_4130905704562196471[212] = 0;
   out_4130905704562196471[213] = 0;
   out_4130905704562196471[214] = 0;
   out_4130905704562196471[215] = 0;
   out_4130905704562196471[216] = 0;
   out_4130905704562196471[217] = 0;
   out_4130905704562196471[218] = 0;
   out_4130905704562196471[219] = 0;
   out_4130905704562196471[220] = 0;
   out_4130905704562196471[221] = 0;
   out_4130905704562196471[222] = 0;
   out_4130905704562196471[223] = 0;
   out_4130905704562196471[224] = 0;
   out_4130905704562196471[225] = 0;
   out_4130905704562196471[226] = 0;
   out_4130905704562196471[227] = 0;
   out_4130905704562196471[228] = 1;
   out_4130905704562196471[229] = 0;
   out_4130905704562196471[230] = 0;
   out_4130905704562196471[231] = 0;
   out_4130905704562196471[232] = 0;
   out_4130905704562196471[233] = 0;
   out_4130905704562196471[234] = 0;
   out_4130905704562196471[235] = 0;
   out_4130905704562196471[236] = 0;
   out_4130905704562196471[237] = 0;
   out_4130905704562196471[238] = 0;
   out_4130905704562196471[239] = 0;
   out_4130905704562196471[240] = 0;
   out_4130905704562196471[241] = 0;
   out_4130905704562196471[242] = 0;
   out_4130905704562196471[243] = 0;
   out_4130905704562196471[244] = 0;
   out_4130905704562196471[245] = 0;
   out_4130905704562196471[246] = 0;
   out_4130905704562196471[247] = 1;
   out_4130905704562196471[248] = 0;
   out_4130905704562196471[249] = 0;
   out_4130905704562196471[250] = 0;
   out_4130905704562196471[251] = 0;
   out_4130905704562196471[252] = 0;
   out_4130905704562196471[253] = 0;
   out_4130905704562196471[254] = 0;
   out_4130905704562196471[255] = 0;
   out_4130905704562196471[256] = 0;
   out_4130905704562196471[257] = 0;
   out_4130905704562196471[258] = 0;
   out_4130905704562196471[259] = 0;
   out_4130905704562196471[260] = 0;
   out_4130905704562196471[261] = 0;
   out_4130905704562196471[262] = 0;
   out_4130905704562196471[263] = 0;
   out_4130905704562196471[264] = 0;
   out_4130905704562196471[265] = 0;
   out_4130905704562196471[266] = 1;
   out_4130905704562196471[267] = 0;
   out_4130905704562196471[268] = 0;
   out_4130905704562196471[269] = 0;
   out_4130905704562196471[270] = 0;
   out_4130905704562196471[271] = 0;
   out_4130905704562196471[272] = 0;
   out_4130905704562196471[273] = 0;
   out_4130905704562196471[274] = 0;
   out_4130905704562196471[275] = 0;
   out_4130905704562196471[276] = 0;
   out_4130905704562196471[277] = 0;
   out_4130905704562196471[278] = 0;
   out_4130905704562196471[279] = 0;
   out_4130905704562196471[280] = 0;
   out_4130905704562196471[281] = 0;
   out_4130905704562196471[282] = 0;
   out_4130905704562196471[283] = 0;
   out_4130905704562196471[284] = 0;
   out_4130905704562196471[285] = 1;
   out_4130905704562196471[286] = 0;
   out_4130905704562196471[287] = 0;
   out_4130905704562196471[288] = 0;
   out_4130905704562196471[289] = 0;
   out_4130905704562196471[290] = 0;
   out_4130905704562196471[291] = 0;
   out_4130905704562196471[292] = 0;
   out_4130905704562196471[293] = 0;
   out_4130905704562196471[294] = 0;
   out_4130905704562196471[295] = 0;
   out_4130905704562196471[296] = 0;
   out_4130905704562196471[297] = 0;
   out_4130905704562196471[298] = 0;
   out_4130905704562196471[299] = 0;
   out_4130905704562196471[300] = 0;
   out_4130905704562196471[301] = 0;
   out_4130905704562196471[302] = 0;
   out_4130905704562196471[303] = 0;
   out_4130905704562196471[304] = 1;
   out_4130905704562196471[305] = 0;
   out_4130905704562196471[306] = 0;
   out_4130905704562196471[307] = 0;
   out_4130905704562196471[308] = 0;
   out_4130905704562196471[309] = 0;
   out_4130905704562196471[310] = 0;
   out_4130905704562196471[311] = 0;
   out_4130905704562196471[312] = 0;
   out_4130905704562196471[313] = 0;
   out_4130905704562196471[314] = 0;
   out_4130905704562196471[315] = 0;
   out_4130905704562196471[316] = 0;
   out_4130905704562196471[317] = 0;
   out_4130905704562196471[318] = 0;
   out_4130905704562196471[319] = 0;
   out_4130905704562196471[320] = 0;
   out_4130905704562196471[321] = 0;
   out_4130905704562196471[322] = 0;
   out_4130905704562196471[323] = 1;
}
void h_4(double *state, double *unused, double *out_3512950417453688471) {
   out_3512950417453688471[0] = state[6] + state[9];
   out_3512950417453688471[1] = state[7] + state[10];
   out_3512950417453688471[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_7223602123241246695) {
   out_7223602123241246695[0] = 0;
   out_7223602123241246695[1] = 0;
   out_7223602123241246695[2] = 0;
   out_7223602123241246695[3] = 0;
   out_7223602123241246695[4] = 0;
   out_7223602123241246695[5] = 0;
   out_7223602123241246695[6] = 1;
   out_7223602123241246695[7] = 0;
   out_7223602123241246695[8] = 0;
   out_7223602123241246695[9] = 1;
   out_7223602123241246695[10] = 0;
   out_7223602123241246695[11] = 0;
   out_7223602123241246695[12] = 0;
   out_7223602123241246695[13] = 0;
   out_7223602123241246695[14] = 0;
   out_7223602123241246695[15] = 0;
   out_7223602123241246695[16] = 0;
   out_7223602123241246695[17] = 0;
   out_7223602123241246695[18] = 0;
   out_7223602123241246695[19] = 0;
   out_7223602123241246695[20] = 0;
   out_7223602123241246695[21] = 0;
   out_7223602123241246695[22] = 0;
   out_7223602123241246695[23] = 0;
   out_7223602123241246695[24] = 0;
   out_7223602123241246695[25] = 1;
   out_7223602123241246695[26] = 0;
   out_7223602123241246695[27] = 0;
   out_7223602123241246695[28] = 1;
   out_7223602123241246695[29] = 0;
   out_7223602123241246695[30] = 0;
   out_7223602123241246695[31] = 0;
   out_7223602123241246695[32] = 0;
   out_7223602123241246695[33] = 0;
   out_7223602123241246695[34] = 0;
   out_7223602123241246695[35] = 0;
   out_7223602123241246695[36] = 0;
   out_7223602123241246695[37] = 0;
   out_7223602123241246695[38] = 0;
   out_7223602123241246695[39] = 0;
   out_7223602123241246695[40] = 0;
   out_7223602123241246695[41] = 0;
   out_7223602123241246695[42] = 0;
   out_7223602123241246695[43] = 0;
   out_7223602123241246695[44] = 1;
   out_7223602123241246695[45] = 0;
   out_7223602123241246695[46] = 0;
   out_7223602123241246695[47] = 1;
   out_7223602123241246695[48] = 0;
   out_7223602123241246695[49] = 0;
   out_7223602123241246695[50] = 0;
   out_7223602123241246695[51] = 0;
   out_7223602123241246695[52] = 0;
   out_7223602123241246695[53] = 0;
}
void h_10(double *state, double *unused, double *out_9200925151251471853) {
   out_9200925151251471853[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_9200925151251471853[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_9200925151251471853[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_3716827504774369733) {
   out_3716827504774369733[0] = 0;
   out_3716827504774369733[1] = 9.8100000000000005*cos(state[1]);
   out_3716827504774369733[2] = 0;
   out_3716827504774369733[3] = 0;
   out_3716827504774369733[4] = -state[8];
   out_3716827504774369733[5] = state[7];
   out_3716827504774369733[6] = 0;
   out_3716827504774369733[7] = state[5];
   out_3716827504774369733[8] = -state[4];
   out_3716827504774369733[9] = 0;
   out_3716827504774369733[10] = 0;
   out_3716827504774369733[11] = 0;
   out_3716827504774369733[12] = 1;
   out_3716827504774369733[13] = 0;
   out_3716827504774369733[14] = 0;
   out_3716827504774369733[15] = 1;
   out_3716827504774369733[16] = 0;
   out_3716827504774369733[17] = 0;
   out_3716827504774369733[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_3716827504774369733[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_3716827504774369733[20] = 0;
   out_3716827504774369733[21] = state[8];
   out_3716827504774369733[22] = 0;
   out_3716827504774369733[23] = -state[6];
   out_3716827504774369733[24] = -state[5];
   out_3716827504774369733[25] = 0;
   out_3716827504774369733[26] = state[3];
   out_3716827504774369733[27] = 0;
   out_3716827504774369733[28] = 0;
   out_3716827504774369733[29] = 0;
   out_3716827504774369733[30] = 0;
   out_3716827504774369733[31] = 1;
   out_3716827504774369733[32] = 0;
   out_3716827504774369733[33] = 0;
   out_3716827504774369733[34] = 1;
   out_3716827504774369733[35] = 0;
   out_3716827504774369733[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_3716827504774369733[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_3716827504774369733[38] = 0;
   out_3716827504774369733[39] = -state[7];
   out_3716827504774369733[40] = state[6];
   out_3716827504774369733[41] = 0;
   out_3716827504774369733[42] = state[4];
   out_3716827504774369733[43] = -state[3];
   out_3716827504774369733[44] = 0;
   out_3716827504774369733[45] = 0;
   out_3716827504774369733[46] = 0;
   out_3716827504774369733[47] = 0;
   out_3716827504774369733[48] = 0;
   out_3716827504774369733[49] = 0;
   out_3716827504774369733[50] = 1;
   out_3716827504774369733[51] = 0;
   out_3716827504774369733[52] = 0;
   out_3716827504774369733[53] = 1;
}
void h_13(double *state, double *unused, double *out_7407158574033381569) {
   out_7407158574033381569[0] = state[3];
   out_7407158574033381569[1] = state[4];
   out_7407158574033381569[2] = state[5];
}
void H_13(double *state, double *unused, double *out_3389846659938722671) {
   out_3389846659938722671[0] = 0;
   out_3389846659938722671[1] = 0;
   out_3389846659938722671[2] = 0;
   out_3389846659938722671[3] = 1;
   out_3389846659938722671[4] = 0;
   out_3389846659938722671[5] = 0;
   out_3389846659938722671[6] = 0;
   out_3389846659938722671[7] = 0;
   out_3389846659938722671[8] = 0;
   out_3389846659938722671[9] = 0;
   out_3389846659938722671[10] = 0;
   out_3389846659938722671[11] = 0;
   out_3389846659938722671[12] = 0;
   out_3389846659938722671[13] = 0;
   out_3389846659938722671[14] = 0;
   out_3389846659938722671[15] = 0;
   out_3389846659938722671[16] = 0;
   out_3389846659938722671[17] = 0;
   out_3389846659938722671[18] = 0;
   out_3389846659938722671[19] = 0;
   out_3389846659938722671[20] = 0;
   out_3389846659938722671[21] = 0;
   out_3389846659938722671[22] = 1;
   out_3389846659938722671[23] = 0;
   out_3389846659938722671[24] = 0;
   out_3389846659938722671[25] = 0;
   out_3389846659938722671[26] = 0;
   out_3389846659938722671[27] = 0;
   out_3389846659938722671[28] = 0;
   out_3389846659938722671[29] = 0;
   out_3389846659938722671[30] = 0;
   out_3389846659938722671[31] = 0;
   out_3389846659938722671[32] = 0;
   out_3389846659938722671[33] = 0;
   out_3389846659938722671[34] = 0;
   out_3389846659938722671[35] = 0;
   out_3389846659938722671[36] = 0;
   out_3389846659938722671[37] = 0;
   out_3389846659938722671[38] = 0;
   out_3389846659938722671[39] = 0;
   out_3389846659938722671[40] = 0;
   out_3389846659938722671[41] = 1;
   out_3389846659938722671[42] = 0;
   out_3389846659938722671[43] = 0;
   out_3389846659938722671[44] = 0;
   out_3389846659938722671[45] = 0;
   out_3389846659938722671[46] = 0;
   out_3389846659938722671[47] = 0;
   out_3389846659938722671[48] = 0;
   out_3389846659938722671[49] = 0;
   out_3389846659938722671[50] = 0;
   out_3389846659938722671[51] = 0;
   out_3389846659938722671[52] = 0;
   out_3389846659938722671[53] = 0;
}
void h_14(double *state, double *unused, double *out_5563746504250402940) {
   out_5563746504250402940[0] = state[6];
   out_5563746504250402940[1] = state[7];
   out_5563746504250402940[2] = state[8];
}
void H_14(double *state, double *unused, double *out_4140813690945874399) {
   out_4140813690945874399[0] = 0;
   out_4140813690945874399[1] = 0;
   out_4140813690945874399[2] = 0;
   out_4140813690945874399[3] = 0;
   out_4140813690945874399[4] = 0;
   out_4140813690945874399[5] = 0;
   out_4140813690945874399[6] = 1;
   out_4140813690945874399[7] = 0;
   out_4140813690945874399[8] = 0;
   out_4140813690945874399[9] = 0;
   out_4140813690945874399[10] = 0;
   out_4140813690945874399[11] = 0;
   out_4140813690945874399[12] = 0;
   out_4140813690945874399[13] = 0;
   out_4140813690945874399[14] = 0;
   out_4140813690945874399[15] = 0;
   out_4140813690945874399[16] = 0;
   out_4140813690945874399[17] = 0;
   out_4140813690945874399[18] = 0;
   out_4140813690945874399[19] = 0;
   out_4140813690945874399[20] = 0;
   out_4140813690945874399[21] = 0;
   out_4140813690945874399[22] = 0;
   out_4140813690945874399[23] = 0;
   out_4140813690945874399[24] = 0;
   out_4140813690945874399[25] = 1;
   out_4140813690945874399[26] = 0;
   out_4140813690945874399[27] = 0;
   out_4140813690945874399[28] = 0;
   out_4140813690945874399[29] = 0;
   out_4140813690945874399[30] = 0;
   out_4140813690945874399[31] = 0;
   out_4140813690945874399[32] = 0;
   out_4140813690945874399[33] = 0;
   out_4140813690945874399[34] = 0;
   out_4140813690945874399[35] = 0;
   out_4140813690945874399[36] = 0;
   out_4140813690945874399[37] = 0;
   out_4140813690945874399[38] = 0;
   out_4140813690945874399[39] = 0;
   out_4140813690945874399[40] = 0;
   out_4140813690945874399[41] = 0;
   out_4140813690945874399[42] = 0;
   out_4140813690945874399[43] = 0;
   out_4140813690945874399[44] = 1;
   out_4140813690945874399[45] = 0;
   out_4140813690945874399[46] = 0;
   out_4140813690945874399[47] = 0;
   out_4140813690945874399[48] = 0;
   out_4140813690945874399[49] = 0;
   out_4140813690945874399[50] = 0;
   out_4140813690945874399[51] = 0;
   out_4140813690945874399[52] = 0;
   out_4140813690945874399[53] = 0;
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

void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_4, H_4, NULL, in_z, in_R, in_ea, MAHA_THRESH_4);
}
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_10, H_10, NULL, in_z, in_R, in_ea, MAHA_THRESH_10);
}
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_13, H_13, NULL, in_z, in_R, in_ea, MAHA_THRESH_13);
}
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_14, H_14, NULL, in_z, in_R, in_ea, MAHA_THRESH_14);
}
void pose_err_fun(double *nom_x, double *delta_x, double *out_5456529213378525094) {
  err_fun(nom_x, delta_x, out_5456529213378525094);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5389676744893681967) {
  inv_err_fun(nom_x, true_x, out_5389676744893681967);
}
void pose_H_mod_fun(double *state, double *out_6025654641358348591) {
  H_mod_fun(state, out_6025654641358348591);
}
void pose_f_fun(double *state, double dt, double *out_8477885110547017436) {
  f_fun(state,  dt, out_8477885110547017436);
}
void pose_F_fun(double *state, double dt, double *out_4130905704562196471) {
  F_fun(state,  dt, out_4130905704562196471);
}
void pose_h_4(double *state, double *unused, double *out_3512950417453688471) {
  h_4(state, unused, out_3512950417453688471);
}
void pose_H_4(double *state, double *unused, double *out_7223602123241246695) {
  H_4(state, unused, out_7223602123241246695);
}
void pose_h_10(double *state, double *unused, double *out_9200925151251471853) {
  h_10(state, unused, out_9200925151251471853);
}
void pose_H_10(double *state, double *unused, double *out_3716827504774369733) {
  H_10(state, unused, out_3716827504774369733);
}
void pose_h_13(double *state, double *unused, double *out_7407158574033381569) {
  h_13(state, unused, out_7407158574033381569);
}
void pose_H_13(double *state, double *unused, double *out_3389846659938722671) {
  H_13(state, unused, out_3389846659938722671);
}
void pose_h_14(double *state, double *unused, double *out_5563746504250402940) {
  h_14(state, unused, out_5563746504250402940);
}
void pose_H_14(double *state, double *unused, double *out_4140813690945874399) {
  H_14(state, unused, out_4140813690945874399);
}
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
}

const EKF pose = {
  .name = "pose",
  .kinds = { 4, 10, 13, 14 },
  .feature_kinds = {  },
  .f_fun = pose_f_fun,
  .F_fun = pose_F_fun,
  .err_fun = pose_err_fun,
  .inv_err_fun = pose_inv_err_fun,
  .H_mod_fun = pose_H_mod_fun,
  .predict = pose_predict,
  .hs = {
    { 4, pose_h_4 },
    { 10, pose_h_10 },
    { 13, pose_h_13 },
    { 14, pose_h_14 },
  },
  .Hs = {
    { 4, pose_H_4 },
    { 10, pose_H_10 },
    { 13, pose_H_13 },
    { 14, pose_H_14 },
  },
  .updates = {
    { 4, pose_update_4 },
    { 10, pose_update_10 },
    { 13, pose_update_13 },
    { 14, pose_update_14 },
  },
  .Hes = {
  },
  .sets = {
  },
  .extra_routines = {
  },
};

ekf_lib_init(pose)
