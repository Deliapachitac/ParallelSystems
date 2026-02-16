#include "dli.h"

void update_hx(int n, float dx, float dy, float dt, thrust::device_vector<float> &hx,
               thrust::device_vector<float> &ez) {
   auto zip_start = thrust::make_zip_iterator(ez.begin() + n, ez.begin());
  thrust::transform(thrust::device, hx.begin(), hx.end() - n, zip_start, hx.begin(),
                 [dt, dx, dy] __device__(float h, thrust::tuple<float, float> t) {
                    float cex = thrust::get<0>(t) - thrust::get<1>(t);
                   return h - dli::C0 * dt / 1.3f * cex / dy;
                 });
}

void update_hy(int n, float dx, float dy, float dt, thrust::device_vector<float> &hy,
               thrust::device_vector<float> &ez) {
                   

    auto zip_start = thrust::make_zip_iterator(ez.begin(), ez.begin() + 1);

  thrust::transform(thrust::device, hy.begin(), hy.end() - 1, zip_start, hy.begin(),
                 [dt, dx, dy]__device__(float h, thrust::tuple<float, float> t) {
                    float cey = thrust::get<0>(t) - thrust::get<1>(t);
                   return h - dli::C0 * dt / 1.3f * cey / dx;
                 });
}

void update_dz(int n, float dx, float dy, float dt, thrust::device_vector<float> &hx_vec,
               thrust::device_vector<float> &hy_vec, thrust::device_vector<float> &dz_vec,
               thrust::counting_iterator<int> &cell_start,
                thrust::counting_iterator<int> &cell_end) {
  auto hx = hx_vec.begin();
  auto hy = hy_vec.begin();
  auto dz = dz_vec.begin();

  thrust::for_each(thrust::device, cell_start, cell_end,
                [n, dx, dy, dt, hx, hy, dz]__device__(int cell_id) {
                  if (cell_id > n) {
                    float hx_diff = hx[cell_id - n] - hx[cell_id];
                    float hy_diff = hy[cell_id] - hy[cell_id - 1];
                    dz[cell_id] += dli::C0 * dt * (hx_diff / dx + hy_diff / dy);
                  }
                });
}


void update_ez(thrust::device_vector<float> &ez, thrust::device_vector<float> &dz) {
  thrust::transform(thrust::device, dz.begin(), dz.end(), ez.begin(),
                 [] __device__ (float d) { return d / 1.3f; });
}



// Do not change the signature of this function
void simulate(int cells_along_dimension, float dx, float dy, float dt,
              thrust::device_vector<float> &d_hx,
              thrust::device_vector<float> &d_hy,
              thrust::device_vector<float> &d_dz,
              thrust::device_vector<float> &d_ez) {
  int cells = cells_along_dimension * cells_along_dimension;
  thrust::counting_iterator<int> cell_start(0);
thrust::counting_iterator<int> cell_end(cells);

  for (int step = 0; step < dli::steps; step++) {
    update_hx(cells_along_dimension, dx, dy, dt, d_hx, d_ez);
    update_hy(cells_along_dimension, dx, dy, dt, d_hy, d_ez);
    update_dz(cells_along_dimension, dx, dy, dt, d_hx, d_hy, d_dz, cell_start, cell_end);
    update_ez(d_ez, d_dz);
  }
}