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
void err_fun(double *nom_x, double *delta_x, double *out_7083424895904025255) {
   out_7083424895904025255[0] = delta_x[0] + nom_x[0];
   out_7083424895904025255[1] = delta_x[1] + nom_x[1];
   out_7083424895904025255[2] = delta_x[2] + nom_x[2];
   out_7083424895904025255[3] = delta_x[3] + nom_x[3];
   out_7083424895904025255[4] = delta_x[4] + nom_x[4];
   out_7083424895904025255[5] = delta_x[5] + nom_x[5];
   out_7083424895904025255[6] = delta_x[6] + nom_x[6];
   out_7083424895904025255[7] = delta_x[7] + nom_x[7];
   out_7083424895904025255[8] = delta_x[8] + nom_x[8];
   out_7083424895904025255[9] = delta_x[9] + nom_x[9];
   out_7083424895904025255[10] = delta_x[10] + nom_x[10];
   out_7083424895904025255[11] = delta_x[11] + nom_x[11];
   out_7083424895904025255[12] = delta_x[12] + nom_x[12];
   out_7083424895904025255[13] = delta_x[13] + nom_x[13];
   out_7083424895904025255[14] = delta_x[14] + nom_x[14];
   out_7083424895904025255[15] = delta_x[15] + nom_x[15];
   out_7083424895904025255[16] = delta_x[16] + nom_x[16];
   out_7083424895904025255[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6838748995040044771) {
   out_6838748995040044771[0] = -nom_x[0] + true_x[0];
   out_6838748995040044771[1] = -nom_x[1] + true_x[1];
   out_6838748995040044771[2] = -nom_x[2] + true_x[2];
   out_6838748995040044771[3] = -nom_x[3] + true_x[3];
   out_6838748995040044771[4] = -nom_x[4] + true_x[4];
   out_6838748995040044771[5] = -nom_x[5] + true_x[5];
   out_6838748995040044771[6] = -nom_x[6] + true_x[6];
   out_6838748995040044771[7] = -nom_x[7] + true_x[7];
   out_6838748995040044771[8] = -nom_x[8] + true_x[8];
   out_6838748995040044771[9] = -nom_x[9] + true_x[9];
   out_6838748995040044771[10] = -nom_x[10] + true_x[10];
   out_6838748995040044771[11] = -nom_x[11] + true_x[11];
   out_6838748995040044771[12] = -nom_x[12] + true_x[12];
   out_6838748995040044771[13] = -nom_x[13] + true_x[13];
   out_6838748995040044771[14] = -nom_x[14] + true_x[14];
   out_6838748995040044771[15] = -nom_x[15] + true_x[15];
   out_6838748995040044771[16] = -nom_x[16] + true_x[16];
   out_6838748995040044771[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_1547699279302149631) {
   out_1547699279302149631[0] = 1.0;
   out_1547699279302149631[1] = 0.0;
   out_1547699279302149631[2] = 0.0;
   out_1547699279302149631[3] = 0.0;
   out_1547699279302149631[4] = 0.0;
   out_1547699279302149631[5] = 0.0;
   out_1547699279302149631[6] = 0.0;
   out_1547699279302149631[7] = 0.0;
   out_1547699279302149631[8] = 0.0;
   out_1547699279302149631[9] = 0.0;
   out_1547699279302149631[10] = 0.0;
   out_1547699279302149631[11] = 0.0;
   out_1547699279302149631[12] = 0.0;
   out_1547699279302149631[13] = 0.0;
   out_1547699279302149631[14] = 0.0;
   out_1547699279302149631[15] = 0.0;
   out_1547699279302149631[16] = 0.0;
   out_1547699279302149631[17] = 0.0;
   out_1547699279302149631[18] = 0.0;
   out_1547699279302149631[19] = 1.0;
   out_1547699279302149631[20] = 0.0;
   out_1547699279302149631[21] = 0.0;
   out_1547699279302149631[22] = 0.0;
   out_1547699279302149631[23] = 0.0;
   out_1547699279302149631[24] = 0.0;
   out_1547699279302149631[25] = 0.0;
   out_1547699279302149631[26] = 0.0;
   out_1547699279302149631[27] = 0.0;
   out_1547699279302149631[28] = 0.0;
   out_1547699279302149631[29] = 0.0;
   out_1547699279302149631[30] = 0.0;
   out_1547699279302149631[31] = 0.0;
   out_1547699279302149631[32] = 0.0;
   out_1547699279302149631[33] = 0.0;
   out_1547699279302149631[34] = 0.0;
   out_1547699279302149631[35] = 0.0;
   out_1547699279302149631[36] = 0.0;
   out_1547699279302149631[37] = 0.0;
   out_1547699279302149631[38] = 1.0;
   out_1547699279302149631[39] = 0.0;
   out_1547699279302149631[40] = 0.0;
   out_1547699279302149631[41] = 0.0;
   out_1547699279302149631[42] = 0.0;
   out_1547699279302149631[43] = 0.0;
   out_1547699279302149631[44] = 0.0;
   out_1547699279302149631[45] = 0.0;
   out_1547699279302149631[46] = 0.0;
   out_1547699279302149631[47] = 0.0;
   out_1547699279302149631[48] = 0.0;
   out_1547699279302149631[49] = 0.0;
   out_1547699279302149631[50] = 0.0;
   out_1547699279302149631[51] = 0.0;
   out_1547699279302149631[52] = 0.0;
   out_1547699279302149631[53] = 0.0;
   out_1547699279302149631[54] = 0.0;
   out_1547699279302149631[55] = 0.0;
   out_1547699279302149631[56] = 0.0;
   out_1547699279302149631[57] = 1.0;
   out_1547699279302149631[58] = 0.0;
   out_1547699279302149631[59] = 0.0;
   out_1547699279302149631[60] = 0.0;
   out_1547699279302149631[61] = 0.0;
   out_1547699279302149631[62] = 0.0;
   out_1547699279302149631[63] = 0.0;
   out_1547699279302149631[64] = 0.0;
   out_1547699279302149631[65] = 0.0;
   out_1547699279302149631[66] = 0.0;
   out_1547699279302149631[67] = 0.0;
   out_1547699279302149631[68] = 0.0;
   out_1547699279302149631[69] = 0.0;
   out_1547699279302149631[70] = 0.0;
   out_1547699279302149631[71] = 0.0;
   out_1547699279302149631[72] = 0.0;
   out_1547699279302149631[73] = 0.0;
   out_1547699279302149631[74] = 0.0;
   out_1547699279302149631[75] = 0.0;
   out_1547699279302149631[76] = 1.0;
   out_1547699279302149631[77] = 0.0;
   out_1547699279302149631[78] = 0.0;
   out_1547699279302149631[79] = 0.0;
   out_1547699279302149631[80] = 0.0;
   out_1547699279302149631[81] = 0.0;
   out_1547699279302149631[82] = 0.0;
   out_1547699279302149631[83] = 0.0;
   out_1547699279302149631[84] = 0.0;
   out_1547699279302149631[85] = 0.0;
   out_1547699279302149631[86] = 0.0;
   out_1547699279302149631[87] = 0.0;
   out_1547699279302149631[88] = 0.0;
   out_1547699279302149631[89] = 0.0;
   out_1547699279302149631[90] = 0.0;
   out_1547699279302149631[91] = 0.0;
   out_1547699279302149631[92] = 0.0;
   out_1547699279302149631[93] = 0.0;
   out_1547699279302149631[94] = 0.0;
   out_1547699279302149631[95] = 1.0;
   out_1547699279302149631[96] = 0.0;
   out_1547699279302149631[97] = 0.0;
   out_1547699279302149631[98] = 0.0;
   out_1547699279302149631[99] = 0.0;
   out_1547699279302149631[100] = 0.0;
   out_1547699279302149631[101] = 0.0;
   out_1547699279302149631[102] = 0.0;
   out_1547699279302149631[103] = 0.0;
   out_1547699279302149631[104] = 0.0;
   out_1547699279302149631[105] = 0.0;
   out_1547699279302149631[106] = 0.0;
   out_1547699279302149631[107] = 0.0;
   out_1547699279302149631[108] = 0.0;
   out_1547699279302149631[109] = 0.0;
   out_1547699279302149631[110] = 0.0;
   out_1547699279302149631[111] = 0.0;
   out_1547699279302149631[112] = 0.0;
   out_1547699279302149631[113] = 0.0;
   out_1547699279302149631[114] = 1.0;
   out_1547699279302149631[115] = 0.0;
   out_1547699279302149631[116] = 0.0;
   out_1547699279302149631[117] = 0.0;
   out_1547699279302149631[118] = 0.0;
   out_1547699279302149631[119] = 0.0;
   out_1547699279302149631[120] = 0.0;
   out_1547699279302149631[121] = 0.0;
   out_1547699279302149631[122] = 0.0;
   out_1547699279302149631[123] = 0.0;
   out_1547699279302149631[124] = 0.0;
   out_1547699279302149631[125] = 0.0;
   out_1547699279302149631[126] = 0.0;
   out_1547699279302149631[127] = 0.0;
   out_1547699279302149631[128] = 0.0;
   out_1547699279302149631[129] = 0.0;
   out_1547699279302149631[130] = 0.0;
   out_1547699279302149631[131] = 0.0;
   out_1547699279302149631[132] = 0.0;
   out_1547699279302149631[133] = 1.0;
   out_1547699279302149631[134] = 0.0;
   out_1547699279302149631[135] = 0.0;
   out_1547699279302149631[136] = 0.0;
   out_1547699279302149631[137] = 0.0;
   out_1547699279302149631[138] = 0.0;
   out_1547699279302149631[139] = 0.0;
   out_1547699279302149631[140] = 0.0;
   out_1547699279302149631[141] = 0.0;
   out_1547699279302149631[142] = 0.0;
   out_1547699279302149631[143] = 0.0;
   out_1547699279302149631[144] = 0.0;
   out_1547699279302149631[145] = 0.0;
   out_1547699279302149631[146] = 0.0;
   out_1547699279302149631[147] = 0.0;
   out_1547699279302149631[148] = 0.0;
   out_1547699279302149631[149] = 0.0;
   out_1547699279302149631[150] = 0.0;
   out_1547699279302149631[151] = 0.0;
   out_1547699279302149631[152] = 1.0;
   out_1547699279302149631[153] = 0.0;
   out_1547699279302149631[154] = 0.0;
   out_1547699279302149631[155] = 0.0;
   out_1547699279302149631[156] = 0.0;
   out_1547699279302149631[157] = 0.0;
   out_1547699279302149631[158] = 0.0;
   out_1547699279302149631[159] = 0.0;
   out_1547699279302149631[160] = 0.0;
   out_1547699279302149631[161] = 0.0;
   out_1547699279302149631[162] = 0.0;
   out_1547699279302149631[163] = 0.0;
   out_1547699279302149631[164] = 0.0;
   out_1547699279302149631[165] = 0.0;
   out_1547699279302149631[166] = 0.0;
   out_1547699279302149631[167] = 0.0;
   out_1547699279302149631[168] = 0.0;
   out_1547699279302149631[169] = 0.0;
   out_1547699279302149631[170] = 0.0;
   out_1547699279302149631[171] = 1.0;
   out_1547699279302149631[172] = 0.0;
   out_1547699279302149631[173] = 0.0;
   out_1547699279302149631[174] = 0.0;
   out_1547699279302149631[175] = 0.0;
   out_1547699279302149631[176] = 0.0;
   out_1547699279302149631[177] = 0.0;
   out_1547699279302149631[178] = 0.0;
   out_1547699279302149631[179] = 0.0;
   out_1547699279302149631[180] = 0.0;
   out_1547699279302149631[181] = 0.0;
   out_1547699279302149631[182] = 0.0;
   out_1547699279302149631[183] = 0.0;
   out_1547699279302149631[184] = 0.0;
   out_1547699279302149631[185] = 0.0;
   out_1547699279302149631[186] = 0.0;
   out_1547699279302149631[187] = 0.0;
   out_1547699279302149631[188] = 0.0;
   out_1547699279302149631[189] = 0.0;
   out_1547699279302149631[190] = 1.0;
   out_1547699279302149631[191] = 0.0;
   out_1547699279302149631[192] = 0.0;
   out_1547699279302149631[193] = 0.0;
   out_1547699279302149631[194] = 0.0;
   out_1547699279302149631[195] = 0.0;
   out_1547699279302149631[196] = 0.0;
   out_1547699279302149631[197] = 0.0;
   out_1547699279302149631[198] = 0.0;
   out_1547699279302149631[199] = 0.0;
   out_1547699279302149631[200] = 0.0;
   out_1547699279302149631[201] = 0.0;
   out_1547699279302149631[202] = 0.0;
   out_1547699279302149631[203] = 0.0;
   out_1547699279302149631[204] = 0.0;
   out_1547699279302149631[205] = 0.0;
   out_1547699279302149631[206] = 0.0;
   out_1547699279302149631[207] = 0.0;
   out_1547699279302149631[208] = 0.0;
   out_1547699279302149631[209] = 1.0;
   out_1547699279302149631[210] = 0.0;
   out_1547699279302149631[211] = 0.0;
   out_1547699279302149631[212] = 0.0;
   out_1547699279302149631[213] = 0.0;
   out_1547699279302149631[214] = 0.0;
   out_1547699279302149631[215] = 0.0;
   out_1547699279302149631[216] = 0.0;
   out_1547699279302149631[217] = 0.0;
   out_1547699279302149631[218] = 0.0;
   out_1547699279302149631[219] = 0.0;
   out_1547699279302149631[220] = 0.0;
   out_1547699279302149631[221] = 0.0;
   out_1547699279302149631[222] = 0.0;
   out_1547699279302149631[223] = 0.0;
   out_1547699279302149631[224] = 0.0;
   out_1547699279302149631[225] = 0.0;
   out_1547699279302149631[226] = 0.0;
   out_1547699279302149631[227] = 0.0;
   out_1547699279302149631[228] = 1.0;
   out_1547699279302149631[229] = 0.0;
   out_1547699279302149631[230] = 0.0;
   out_1547699279302149631[231] = 0.0;
   out_1547699279302149631[232] = 0.0;
   out_1547699279302149631[233] = 0.0;
   out_1547699279302149631[234] = 0.0;
   out_1547699279302149631[235] = 0.0;
   out_1547699279302149631[236] = 0.0;
   out_1547699279302149631[237] = 0.0;
   out_1547699279302149631[238] = 0.0;
   out_1547699279302149631[239] = 0.0;
   out_1547699279302149631[240] = 0.0;
   out_1547699279302149631[241] = 0.0;
   out_1547699279302149631[242] = 0.0;
   out_1547699279302149631[243] = 0.0;
   out_1547699279302149631[244] = 0.0;
   out_1547699279302149631[245] = 0.0;
   out_1547699279302149631[246] = 0.0;
   out_1547699279302149631[247] = 1.0;
   out_1547699279302149631[248] = 0.0;
   out_1547699279302149631[249] = 0.0;
   out_1547699279302149631[250] = 0.0;
   out_1547699279302149631[251] = 0.0;
   out_1547699279302149631[252] = 0.0;
   out_1547699279302149631[253] = 0.0;
   out_1547699279302149631[254] = 0.0;
   out_1547699279302149631[255] = 0.0;
   out_1547699279302149631[256] = 0.0;
   out_1547699279302149631[257] = 0.0;
   out_1547699279302149631[258] = 0.0;
   out_1547699279302149631[259] = 0.0;
   out_1547699279302149631[260] = 0.0;
   out_1547699279302149631[261] = 0.0;
   out_1547699279302149631[262] = 0.0;
   out_1547699279302149631[263] = 0.0;
   out_1547699279302149631[264] = 0.0;
   out_1547699279302149631[265] = 0.0;
   out_1547699279302149631[266] = 1.0;
   out_1547699279302149631[267] = 0.0;
   out_1547699279302149631[268] = 0.0;
   out_1547699279302149631[269] = 0.0;
   out_1547699279302149631[270] = 0.0;
   out_1547699279302149631[271] = 0.0;
   out_1547699279302149631[272] = 0.0;
   out_1547699279302149631[273] = 0.0;
   out_1547699279302149631[274] = 0.0;
   out_1547699279302149631[275] = 0.0;
   out_1547699279302149631[276] = 0.0;
   out_1547699279302149631[277] = 0.0;
   out_1547699279302149631[278] = 0.0;
   out_1547699279302149631[279] = 0.0;
   out_1547699279302149631[280] = 0.0;
   out_1547699279302149631[281] = 0.0;
   out_1547699279302149631[282] = 0.0;
   out_1547699279302149631[283] = 0.0;
   out_1547699279302149631[284] = 0.0;
   out_1547699279302149631[285] = 1.0;
   out_1547699279302149631[286] = 0.0;
   out_1547699279302149631[287] = 0.0;
   out_1547699279302149631[288] = 0.0;
   out_1547699279302149631[289] = 0.0;
   out_1547699279302149631[290] = 0.0;
   out_1547699279302149631[291] = 0.0;
   out_1547699279302149631[292] = 0.0;
   out_1547699279302149631[293] = 0.0;
   out_1547699279302149631[294] = 0.0;
   out_1547699279302149631[295] = 0.0;
   out_1547699279302149631[296] = 0.0;
   out_1547699279302149631[297] = 0.0;
   out_1547699279302149631[298] = 0.0;
   out_1547699279302149631[299] = 0.0;
   out_1547699279302149631[300] = 0.0;
   out_1547699279302149631[301] = 0.0;
   out_1547699279302149631[302] = 0.0;
   out_1547699279302149631[303] = 0.0;
   out_1547699279302149631[304] = 1.0;
   out_1547699279302149631[305] = 0.0;
   out_1547699279302149631[306] = 0.0;
   out_1547699279302149631[307] = 0.0;
   out_1547699279302149631[308] = 0.0;
   out_1547699279302149631[309] = 0.0;
   out_1547699279302149631[310] = 0.0;
   out_1547699279302149631[311] = 0.0;
   out_1547699279302149631[312] = 0.0;
   out_1547699279302149631[313] = 0.0;
   out_1547699279302149631[314] = 0.0;
   out_1547699279302149631[315] = 0.0;
   out_1547699279302149631[316] = 0.0;
   out_1547699279302149631[317] = 0.0;
   out_1547699279302149631[318] = 0.0;
   out_1547699279302149631[319] = 0.0;
   out_1547699279302149631[320] = 0.0;
   out_1547699279302149631[321] = 0.0;
   out_1547699279302149631[322] = 0.0;
   out_1547699279302149631[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_6474378312856621026) {
   out_6474378312856621026[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_6474378312856621026[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_6474378312856621026[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_6474378312856621026[3] = dt*state[12] + state[3];
   out_6474378312856621026[4] = dt*state[13] + state[4];
   out_6474378312856621026[5] = dt*state[14] + state[5];
   out_6474378312856621026[6] = state[6];
   out_6474378312856621026[7] = state[7];
   out_6474378312856621026[8] = state[8];
   out_6474378312856621026[9] = state[9];
   out_6474378312856621026[10] = state[10];
   out_6474378312856621026[11] = state[11];
   out_6474378312856621026[12] = state[12];
   out_6474378312856621026[13] = state[13];
   out_6474378312856621026[14] = state[14];
   out_6474378312856621026[15] = state[15];
   out_6474378312856621026[16] = state[16];
   out_6474378312856621026[17] = state[17];
}
void F_fun(double *state, double dt, double *out_8540366478724720162) {
   out_8540366478724720162[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8540366478724720162[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8540366478724720162[2] = 0;
   out_8540366478724720162[3] = 0;
   out_8540366478724720162[4] = 0;
   out_8540366478724720162[5] = 0;
   out_8540366478724720162[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8540366478724720162[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8540366478724720162[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_8540366478724720162[9] = 0;
   out_8540366478724720162[10] = 0;
   out_8540366478724720162[11] = 0;
   out_8540366478724720162[12] = 0;
   out_8540366478724720162[13] = 0;
   out_8540366478724720162[14] = 0;
   out_8540366478724720162[15] = 0;
   out_8540366478724720162[16] = 0;
   out_8540366478724720162[17] = 0;
   out_8540366478724720162[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8540366478724720162[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8540366478724720162[20] = 0;
   out_8540366478724720162[21] = 0;
   out_8540366478724720162[22] = 0;
   out_8540366478724720162[23] = 0;
   out_8540366478724720162[24] = 0;
   out_8540366478724720162[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8540366478724720162[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_8540366478724720162[27] = 0;
   out_8540366478724720162[28] = 0;
   out_8540366478724720162[29] = 0;
   out_8540366478724720162[30] = 0;
   out_8540366478724720162[31] = 0;
   out_8540366478724720162[32] = 0;
   out_8540366478724720162[33] = 0;
   out_8540366478724720162[34] = 0;
   out_8540366478724720162[35] = 0;
   out_8540366478724720162[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8540366478724720162[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8540366478724720162[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8540366478724720162[39] = 0;
   out_8540366478724720162[40] = 0;
   out_8540366478724720162[41] = 0;
   out_8540366478724720162[42] = 0;
   out_8540366478724720162[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8540366478724720162[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_8540366478724720162[45] = 0;
   out_8540366478724720162[46] = 0;
   out_8540366478724720162[47] = 0;
   out_8540366478724720162[48] = 0;
   out_8540366478724720162[49] = 0;
   out_8540366478724720162[50] = 0;
   out_8540366478724720162[51] = 0;
   out_8540366478724720162[52] = 0;
   out_8540366478724720162[53] = 0;
   out_8540366478724720162[54] = 0;
   out_8540366478724720162[55] = 0;
   out_8540366478724720162[56] = 0;
   out_8540366478724720162[57] = 1;
   out_8540366478724720162[58] = 0;
   out_8540366478724720162[59] = 0;
   out_8540366478724720162[60] = 0;
   out_8540366478724720162[61] = 0;
   out_8540366478724720162[62] = 0;
   out_8540366478724720162[63] = 0;
   out_8540366478724720162[64] = 0;
   out_8540366478724720162[65] = 0;
   out_8540366478724720162[66] = dt;
   out_8540366478724720162[67] = 0;
   out_8540366478724720162[68] = 0;
   out_8540366478724720162[69] = 0;
   out_8540366478724720162[70] = 0;
   out_8540366478724720162[71] = 0;
   out_8540366478724720162[72] = 0;
   out_8540366478724720162[73] = 0;
   out_8540366478724720162[74] = 0;
   out_8540366478724720162[75] = 0;
   out_8540366478724720162[76] = 1;
   out_8540366478724720162[77] = 0;
   out_8540366478724720162[78] = 0;
   out_8540366478724720162[79] = 0;
   out_8540366478724720162[80] = 0;
   out_8540366478724720162[81] = 0;
   out_8540366478724720162[82] = 0;
   out_8540366478724720162[83] = 0;
   out_8540366478724720162[84] = 0;
   out_8540366478724720162[85] = dt;
   out_8540366478724720162[86] = 0;
   out_8540366478724720162[87] = 0;
   out_8540366478724720162[88] = 0;
   out_8540366478724720162[89] = 0;
   out_8540366478724720162[90] = 0;
   out_8540366478724720162[91] = 0;
   out_8540366478724720162[92] = 0;
   out_8540366478724720162[93] = 0;
   out_8540366478724720162[94] = 0;
   out_8540366478724720162[95] = 1;
   out_8540366478724720162[96] = 0;
   out_8540366478724720162[97] = 0;
   out_8540366478724720162[98] = 0;
   out_8540366478724720162[99] = 0;
   out_8540366478724720162[100] = 0;
   out_8540366478724720162[101] = 0;
   out_8540366478724720162[102] = 0;
   out_8540366478724720162[103] = 0;
   out_8540366478724720162[104] = dt;
   out_8540366478724720162[105] = 0;
   out_8540366478724720162[106] = 0;
   out_8540366478724720162[107] = 0;
   out_8540366478724720162[108] = 0;
   out_8540366478724720162[109] = 0;
   out_8540366478724720162[110] = 0;
   out_8540366478724720162[111] = 0;
   out_8540366478724720162[112] = 0;
   out_8540366478724720162[113] = 0;
   out_8540366478724720162[114] = 1;
   out_8540366478724720162[115] = 0;
   out_8540366478724720162[116] = 0;
   out_8540366478724720162[117] = 0;
   out_8540366478724720162[118] = 0;
   out_8540366478724720162[119] = 0;
   out_8540366478724720162[120] = 0;
   out_8540366478724720162[121] = 0;
   out_8540366478724720162[122] = 0;
   out_8540366478724720162[123] = 0;
   out_8540366478724720162[124] = 0;
   out_8540366478724720162[125] = 0;
   out_8540366478724720162[126] = 0;
   out_8540366478724720162[127] = 0;
   out_8540366478724720162[128] = 0;
   out_8540366478724720162[129] = 0;
   out_8540366478724720162[130] = 0;
   out_8540366478724720162[131] = 0;
   out_8540366478724720162[132] = 0;
   out_8540366478724720162[133] = 1;
   out_8540366478724720162[134] = 0;
   out_8540366478724720162[135] = 0;
   out_8540366478724720162[136] = 0;
   out_8540366478724720162[137] = 0;
   out_8540366478724720162[138] = 0;
   out_8540366478724720162[139] = 0;
   out_8540366478724720162[140] = 0;
   out_8540366478724720162[141] = 0;
   out_8540366478724720162[142] = 0;
   out_8540366478724720162[143] = 0;
   out_8540366478724720162[144] = 0;
   out_8540366478724720162[145] = 0;
   out_8540366478724720162[146] = 0;
   out_8540366478724720162[147] = 0;
   out_8540366478724720162[148] = 0;
   out_8540366478724720162[149] = 0;
   out_8540366478724720162[150] = 0;
   out_8540366478724720162[151] = 0;
   out_8540366478724720162[152] = 1;
   out_8540366478724720162[153] = 0;
   out_8540366478724720162[154] = 0;
   out_8540366478724720162[155] = 0;
   out_8540366478724720162[156] = 0;
   out_8540366478724720162[157] = 0;
   out_8540366478724720162[158] = 0;
   out_8540366478724720162[159] = 0;
   out_8540366478724720162[160] = 0;
   out_8540366478724720162[161] = 0;
   out_8540366478724720162[162] = 0;
   out_8540366478724720162[163] = 0;
   out_8540366478724720162[164] = 0;
   out_8540366478724720162[165] = 0;
   out_8540366478724720162[166] = 0;
   out_8540366478724720162[167] = 0;
   out_8540366478724720162[168] = 0;
   out_8540366478724720162[169] = 0;
   out_8540366478724720162[170] = 0;
   out_8540366478724720162[171] = 1;
   out_8540366478724720162[172] = 0;
   out_8540366478724720162[173] = 0;
   out_8540366478724720162[174] = 0;
   out_8540366478724720162[175] = 0;
   out_8540366478724720162[176] = 0;
   out_8540366478724720162[177] = 0;
   out_8540366478724720162[178] = 0;
   out_8540366478724720162[179] = 0;
   out_8540366478724720162[180] = 0;
   out_8540366478724720162[181] = 0;
   out_8540366478724720162[182] = 0;
   out_8540366478724720162[183] = 0;
   out_8540366478724720162[184] = 0;
   out_8540366478724720162[185] = 0;
   out_8540366478724720162[186] = 0;
   out_8540366478724720162[187] = 0;
   out_8540366478724720162[188] = 0;
   out_8540366478724720162[189] = 0;
   out_8540366478724720162[190] = 1;
   out_8540366478724720162[191] = 0;
   out_8540366478724720162[192] = 0;
   out_8540366478724720162[193] = 0;
   out_8540366478724720162[194] = 0;
   out_8540366478724720162[195] = 0;
   out_8540366478724720162[196] = 0;
   out_8540366478724720162[197] = 0;
   out_8540366478724720162[198] = 0;
   out_8540366478724720162[199] = 0;
   out_8540366478724720162[200] = 0;
   out_8540366478724720162[201] = 0;
   out_8540366478724720162[202] = 0;
   out_8540366478724720162[203] = 0;
   out_8540366478724720162[204] = 0;
   out_8540366478724720162[205] = 0;
   out_8540366478724720162[206] = 0;
   out_8540366478724720162[207] = 0;
   out_8540366478724720162[208] = 0;
   out_8540366478724720162[209] = 1;
   out_8540366478724720162[210] = 0;
   out_8540366478724720162[211] = 0;
   out_8540366478724720162[212] = 0;
   out_8540366478724720162[213] = 0;
   out_8540366478724720162[214] = 0;
   out_8540366478724720162[215] = 0;
   out_8540366478724720162[216] = 0;
   out_8540366478724720162[217] = 0;
   out_8540366478724720162[218] = 0;
   out_8540366478724720162[219] = 0;
   out_8540366478724720162[220] = 0;
   out_8540366478724720162[221] = 0;
   out_8540366478724720162[222] = 0;
   out_8540366478724720162[223] = 0;
   out_8540366478724720162[224] = 0;
   out_8540366478724720162[225] = 0;
   out_8540366478724720162[226] = 0;
   out_8540366478724720162[227] = 0;
   out_8540366478724720162[228] = 1;
   out_8540366478724720162[229] = 0;
   out_8540366478724720162[230] = 0;
   out_8540366478724720162[231] = 0;
   out_8540366478724720162[232] = 0;
   out_8540366478724720162[233] = 0;
   out_8540366478724720162[234] = 0;
   out_8540366478724720162[235] = 0;
   out_8540366478724720162[236] = 0;
   out_8540366478724720162[237] = 0;
   out_8540366478724720162[238] = 0;
   out_8540366478724720162[239] = 0;
   out_8540366478724720162[240] = 0;
   out_8540366478724720162[241] = 0;
   out_8540366478724720162[242] = 0;
   out_8540366478724720162[243] = 0;
   out_8540366478724720162[244] = 0;
   out_8540366478724720162[245] = 0;
   out_8540366478724720162[246] = 0;
   out_8540366478724720162[247] = 1;
   out_8540366478724720162[248] = 0;
   out_8540366478724720162[249] = 0;
   out_8540366478724720162[250] = 0;
   out_8540366478724720162[251] = 0;
   out_8540366478724720162[252] = 0;
   out_8540366478724720162[253] = 0;
   out_8540366478724720162[254] = 0;
   out_8540366478724720162[255] = 0;
   out_8540366478724720162[256] = 0;
   out_8540366478724720162[257] = 0;
   out_8540366478724720162[258] = 0;
   out_8540366478724720162[259] = 0;
   out_8540366478724720162[260] = 0;
   out_8540366478724720162[261] = 0;
   out_8540366478724720162[262] = 0;
   out_8540366478724720162[263] = 0;
   out_8540366478724720162[264] = 0;
   out_8540366478724720162[265] = 0;
   out_8540366478724720162[266] = 1;
   out_8540366478724720162[267] = 0;
   out_8540366478724720162[268] = 0;
   out_8540366478724720162[269] = 0;
   out_8540366478724720162[270] = 0;
   out_8540366478724720162[271] = 0;
   out_8540366478724720162[272] = 0;
   out_8540366478724720162[273] = 0;
   out_8540366478724720162[274] = 0;
   out_8540366478724720162[275] = 0;
   out_8540366478724720162[276] = 0;
   out_8540366478724720162[277] = 0;
   out_8540366478724720162[278] = 0;
   out_8540366478724720162[279] = 0;
   out_8540366478724720162[280] = 0;
   out_8540366478724720162[281] = 0;
   out_8540366478724720162[282] = 0;
   out_8540366478724720162[283] = 0;
   out_8540366478724720162[284] = 0;
   out_8540366478724720162[285] = 1;
   out_8540366478724720162[286] = 0;
   out_8540366478724720162[287] = 0;
   out_8540366478724720162[288] = 0;
   out_8540366478724720162[289] = 0;
   out_8540366478724720162[290] = 0;
   out_8540366478724720162[291] = 0;
   out_8540366478724720162[292] = 0;
   out_8540366478724720162[293] = 0;
   out_8540366478724720162[294] = 0;
   out_8540366478724720162[295] = 0;
   out_8540366478724720162[296] = 0;
   out_8540366478724720162[297] = 0;
   out_8540366478724720162[298] = 0;
   out_8540366478724720162[299] = 0;
   out_8540366478724720162[300] = 0;
   out_8540366478724720162[301] = 0;
   out_8540366478724720162[302] = 0;
   out_8540366478724720162[303] = 0;
   out_8540366478724720162[304] = 1;
   out_8540366478724720162[305] = 0;
   out_8540366478724720162[306] = 0;
   out_8540366478724720162[307] = 0;
   out_8540366478724720162[308] = 0;
   out_8540366478724720162[309] = 0;
   out_8540366478724720162[310] = 0;
   out_8540366478724720162[311] = 0;
   out_8540366478724720162[312] = 0;
   out_8540366478724720162[313] = 0;
   out_8540366478724720162[314] = 0;
   out_8540366478724720162[315] = 0;
   out_8540366478724720162[316] = 0;
   out_8540366478724720162[317] = 0;
   out_8540366478724720162[318] = 0;
   out_8540366478724720162[319] = 0;
   out_8540366478724720162[320] = 0;
   out_8540366478724720162[321] = 0;
   out_8540366478724720162[322] = 0;
   out_8540366478724720162[323] = 1;
}
void h_4(double *state, double *unused, double *out_1356905819811932649) {
   out_1356905819811932649[0] = state[6] + state[9];
   out_1356905819811932649[1] = state[7] + state[10];
   out_1356905819811932649[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_793538277247437024) {
   out_793538277247437024[0] = 0;
   out_793538277247437024[1] = 0;
   out_793538277247437024[2] = 0;
   out_793538277247437024[3] = 0;
   out_793538277247437024[4] = 0;
   out_793538277247437024[5] = 0;
   out_793538277247437024[6] = 1;
   out_793538277247437024[7] = 0;
   out_793538277247437024[8] = 0;
   out_793538277247437024[9] = 1;
   out_793538277247437024[10] = 0;
   out_793538277247437024[11] = 0;
   out_793538277247437024[12] = 0;
   out_793538277247437024[13] = 0;
   out_793538277247437024[14] = 0;
   out_793538277247437024[15] = 0;
   out_793538277247437024[16] = 0;
   out_793538277247437024[17] = 0;
   out_793538277247437024[18] = 0;
   out_793538277247437024[19] = 0;
   out_793538277247437024[20] = 0;
   out_793538277247437024[21] = 0;
   out_793538277247437024[22] = 0;
   out_793538277247437024[23] = 0;
   out_793538277247437024[24] = 0;
   out_793538277247437024[25] = 1;
   out_793538277247437024[26] = 0;
   out_793538277247437024[27] = 0;
   out_793538277247437024[28] = 1;
   out_793538277247437024[29] = 0;
   out_793538277247437024[30] = 0;
   out_793538277247437024[31] = 0;
   out_793538277247437024[32] = 0;
   out_793538277247437024[33] = 0;
   out_793538277247437024[34] = 0;
   out_793538277247437024[35] = 0;
   out_793538277247437024[36] = 0;
   out_793538277247437024[37] = 0;
   out_793538277247437024[38] = 0;
   out_793538277247437024[39] = 0;
   out_793538277247437024[40] = 0;
   out_793538277247437024[41] = 0;
   out_793538277247437024[42] = 0;
   out_793538277247437024[43] = 0;
   out_793538277247437024[44] = 1;
   out_793538277247437024[45] = 0;
   out_793538277247437024[46] = 0;
   out_793538277247437024[47] = 1;
   out_793538277247437024[48] = 0;
   out_793538277247437024[49] = 0;
   out_793538277247437024[50] = 0;
   out_793538277247437024[51] = 0;
   out_793538277247437024[52] = 0;
   out_793538277247437024[53] = 0;
}
void h_10(double *state, double *unused, double *out_5351520755944402824) {
   out_5351520755944402824[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_5351520755944402824[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_5351520755944402824[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_1794142950195422749) {
   out_1794142950195422749[0] = 0;
   out_1794142950195422749[1] = 9.8100000000000005*cos(state[1]);
   out_1794142950195422749[2] = 0;
   out_1794142950195422749[3] = 0;
   out_1794142950195422749[4] = -state[8];
   out_1794142950195422749[5] = state[7];
   out_1794142950195422749[6] = 0;
   out_1794142950195422749[7] = state[5];
   out_1794142950195422749[8] = -state[4];
   out_1794142950195422749[9] = 0;
   out_1794142950195422749[10] = 0;
   out_1794142950195422749[11] = 0;
   out_1794142950195422749[12] = 1;
   out_1794142950195422749[13] = 0;
   out_1794142950195422749[14] = 0;
   out_1794142950195422749[15] = 1;
   out_1794142950195422749[16] = 0;
   out_1794142950195422749[17] = 0;
   out_1794142950195422749[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_1794142950195422749[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_1794142950195422749[20] = 0;
   out_1794142950195422749[21] = state[8];
   out_1794142950195422749[22] = 0;
   out_1794142950195422749[23] = -state[6];
   out_1794142950195422749[24] = -state[5];
   out_1794142950195422749[25] = 0;
   out_1794142950195422749[26] = state[3];
   out_1794142950195422749[27] = 0;
   out_1794142950195422749[28] = 0;
   out_1794142950195422749[29] = 0;
   out_1794142950195422749[30] = 0;
   out_1794142950195422749[31] = 1;
   out_1794142950195422749[32] = 0;
   out_1794142950195422749[33] = 0;
   out_1794142950195422749[34] = 1;
   out_1794142950195422749[35] = 0;
   out_1794142950195422749[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_1794142950195422749[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_1794142950195422749[38] = 0;
   out_1794142950195422749[39] = -state[7];
   out_1794142950195422749[40] = state[6];
   out_1794142950195422749[41] = 0;
   out_1794142950195422749[42] = state[4];
   out_1794142950195422749[43] = -state[3];
   out_1794142950195422749[44] = 0;
   out_1794142950195422749[45] = 0;
   out_1794142950195422749[46] = 0;
   out_1794142950195422749[47] = 0;
   out_1794142950195422749[48] = 0;
   out_1794142950195422749[49] = 0;
   out_1794142950195422749[50] = 1;
   out_1794142950195422749[51] = 0;
   out_1794142950195422749[52] = 0;
   out_1794142950195422749[53] = 1;
}
void h_13(double *state, double *unused, double *out_6629156441156146262) {
   out_6629156441156146262[0] = state[3];
   out_6629156441156146262[1] = state[4];
   out_6629156441156146262[2] = state[5];
}
void H_13(double *state, double *unused, double *out_6817092931069263905) {
   out_6817092931069263905[0] = 0;
   out_6817092931069263905[1] = 0;
   out_6817092931069263905[2] = 0;
   out_6817092931069263905[3] = 1;
   out_6817092931069263905[4] = 0;
   out_6817092931069263905[5] = 0;
   out_6817092931069263905[6] = 0;
   out_6817092931069263905[7] = 0;
   out_6817092931069263905[8] = 0;
   out_6817092931069263905[9] = 0;
   out_6817092931069263905[10] = 0;
   out_6817092931069263905[11] = 0;
   out_6817092931069263905[12] = 0;
   out_6817092931069263905[13] = 0;
   out_6817092931069263905[14] = 0;
   out_6817092931069263905[15] = 0;
   out_6817092931069263905[16] = 0;
   out_6817092931069263905[17] = 0;
   out_6817092931069263905[18] = 0;
   out_6817092931069263905[19] = 0;
   out_6817092931069263905[20] = 0;
   out_6817092931069263905[21] = 0;
   out_6817092931069263905[22] = 1;
   out_6817092931069263905[23] = 0;
   out_6817092931069263905[24] = 0;
   out_6817092931069263905[25] = 0;
   out_6817092931069263905[26] = 0;
   out_6817092931069263905[27] = 0;
   out_6817092931069263905[28] = 0;
   out_6817092931069263905[29] = 0;
   out_6817092931069263905[30] = 0;
   out_6817092931069263905[31] = 0;
   out_6817092931069263905[32] = 0;
   out_6817092931069263905[33] = 0;
   out_6817092931069263905[34] = 0;
   out_6817092931069263905[35] = 0;
   out_6817092931069263905[36] = 0;
   out_6817092931069263905[37] = 0;
   out_6817092931069263905[38] = 0;
   out_6817092931069263905[39] = 0;
   out_6817092931069263905[40] = 0;
   out_6817092931069263905[41] = 1;
   out_6817092931069263905[42] = 0;
   out_6817092931069263905[43] = 0;
   out_6817092931069263905[44] = 0;
   out_6817092931069263905[45] = 0;
   out_6817092931069263905[46] = 0;
   out_6817092931069263905[47] = 0;
   out_6817092931069263905[48] = 0;
   out_6817092931069263905[49] = 0;
   out_6817092931069263905[50] = 0;
   out_6817092931069263905[51] = 0;
   out_6817092931069263905[52] = 0;
   out_6817092931069263905[53] = 0;
}
void h_14(double *state, double *unused, double *out_2949760970451347774) {
   out_2949760970451347774[0] = state[6];
   out_2949760970451347774[1] = state[7];
   out_2949760970451347774[2] = state[8];
}
void H_14(double *state, double *unused, double *out_3169702579092047505) {
   out_3169702579092047505[0] = 0;
   out_3169702579092047505[1] = 0;
   out_3169702579092047505[2] = 0;
   out_3169702579092047505[3] = 0;
   out_3169702579092047505[4] = 0;
   out_3169702579092047505[5] = 0;
   out_3169702579092047505[6] = 1;
   out_3169702579092047505[7] = 0;
   out_3169702579092047505[8] = 0;
   out_3169702579092047505[9] = 0;
   out_3169702579092047505[10] = 0;
   out_3169702579092047505[11] = 0;
   out_3169702579092047505[12] = 0;
   out_3169702579092047505[13] = 0;
   out_3169702579092047505[14] = 0;
   out_3169702579092047505[15] = 0;
   out_3169702579092047505[16] = 0;
   out_3169702579092047505[17] = 0;
   out_3169702579092047505[18] = 0;
   out_3169702579092047505[19] = 0;
   out_3169702579092047505[20] = 0;
   out_3169702579092047505[21] = 0;
   out_3169702579092047505[22] = 0;
   out_3169702579092047505[23] = 0;
   out_3169702579092047505[24] = 0;
   out_3169702579092047505[25] = 1;
   out_3169702579092047505[26] = 0;
   out_3169702579092047505[27] = 0;
   out_3169702579092047505[28] = 0;
   out_3169702579092047505[29] = 0;
   out_3169702579092047505[30] = 0;
   out_3169702579092047505[31] = 0;
   out_3169702579092047505[32] = 0;
   out_3169702579092047505[33] = 0;
   out_3169702579092047505[34] = 0;
   out_3169702579092047505[35] = 0;
   out_3169702579092047505[36] = 0;
   out_3169702579092047505[37] = 0;
   out_3169702579092047505[38] = 0;
   out_3169702579092047505[39] = 0;
   out_3169702579092047505[40] = 0;
   out_3169702579092047505[41] = 0;
   out_3169702579092047505[42] = 0;
   out_3169702579092047505[43] = 0;
   out_3169702579092047505[44] = 1;
   out_3169702579092047505[45] = 0;
   out_3169702579092047505[46] = 0;
   out_3169702579092047505[47] = 0;
   out_3169702579092047505[48] = 0;
   out_3169702579092047505[49] = 0;
   out_3169702579092047505[50] = 0;
   out_3169702579092047505[51] = 0;
   out_3169702579092047505[52] = 0;
   out_3169702579092047505[53] = 0;
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
void pose_err_fun(double *nom_x, double *delta_x, double *out_7083424895904025255) {
  err_fun(nom_x, delta_x, out_7083424895904025255);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6838748995040044771) {
  inv_err_fun(nom_x, true_x, out_6838748995040044771);
}
void pose_H_mod_fun(double *state, double *out_1547699279302149631) {
  H_mod_fun(state, out_1547699279302149631);
}
void pose_f_fun(double *state, double dt, double *out_6474378312856621026) {
  f_fun(state,  dt, out_6474378312856621026);
}
void pose_F_fun(double *state, double dt, double *out_8540366478724720162) {
  F_fun(state,  dt, out_8540366478724720162);
}
void pose_h_4(double *state, double *unused, double *out_1356905819811932649) {
  h_4(state, unused, out_1356905819811932649);
}
void pose_H_4(double *state, double *unused, double *out_793538277247437024) {
  H_4(state, unused, out_793538277247437024);
}
void pose_h_10(double *state, double *unused, double *out_5351520755944402824) {
  h_10(state, unused, out_5351520755944402824);
}
void pose_H_10(double *state, double *unused, double *out_1794142950195422749) {
  H_10(state, unused, out_1794142950195422749);
}
void pose_h_13(double *state, double *unused, double *out_6629156441156146262) {
  h_13(state, unused, out_6629156441156146262);
}
void pose_H_13(double *state, double *unused, double *out_6817092931069263905) {
  H_13(state, unused, out_6817092931069263905);
}
void pose_h_14(double *state, double *unused, double *out_2949760970451347774) {
  h_14(state, unused, out_2949760970451347774);
}
void pose_H_14(double *state, double *unused, double *out_3169702579092047505) {
  H_14(state, unused, out_3169702579092047505);
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
