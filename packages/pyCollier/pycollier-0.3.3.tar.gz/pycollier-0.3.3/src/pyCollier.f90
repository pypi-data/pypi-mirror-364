subroutine initialize_fortran(Nmax,rmax,output,noreset)
	use COLLIER
    use collier_global
	implicit none
    integer, optional, intent(in) :: Nmax, rmax
    logical, optional, intent(in) :: output, noreset
    integer :: t_Nmax, t_rmax
    logical :: t_noreset, t_output
    t_Nmax = 4 ! Nmax = maximal degree N of N-point function
    t_rmax = 4 ! rmax = maximal tensor rank
    t_noreset = .false.
    t_output = .false.

    if (present(Nmax).and.(Nmax.gt.0)) then
      t_Nmax = Nmax
    endif
    if (present(rmax).and.(rmax.gt.0)) then
      t_rmax = rmax
    endif
    if (present(output)) then
      t_output = output
    endif
    if(.not.t_output) then
        open(50,file='/dev/null')
        stdout_cll = 50
    endif
    if (present(noreset)) then
      t_noreset = noreset
    endif

    if (t_output) then
        call Init_cll(t_Nmax, t_rmax, "./output_cll", t_noreset)
    else
        call Init_cll(t_Nmax, t_rmax, "", t_noreset)
    endif

end subroutine initialize_fortran

!-------------------------------------------------------------------------------

subroutine set_renscale_fortran(mu2)
	use COLLIER
	implicit none
  double precision, intent(in) :: mu2

	call SetMuUV2_cll(mu2)

end subroutine set_renscale_fortran

!-------------------------------------------------------------------------------

subroutine get_renscale_fortran(mu2)
	use COLLIER
	implicit none

  double precision, intent(out) :: mu2

	call GetMuUV2_cll(mu2)

end subroutine get_renscale_fortran

!-------------------------------------------------------------------------------

subroutine set_delta_fortran(delta)
	use COLLIER
	implicit none
  double precision, intent(in) :: delta

	call SetDeltaUV_cll(delta)

end subroutine set_delta_fortran

!-------------------------------------------------------------------------------

subroutine get_delta_fortran(delta)
	use COLLIER
	implicit none

  double precision, intent(out) :: delta

	call GetDeltaUV_cll(delta)

end subroutine get_delta_fortran

!-------------------------------------------------------------------------------

subroutine set_muIR2_fortran(mu2)
	use COLLIER
	implicit none
  double precision, intent(in) :: mu2

	call SetMuIR2_cll(mu2)

end subroutine set_muIR2_fortran

!-------------------------------------------------------------------------------

subroutine get_muIR2_fortran(mu2)
	use COLLIER
	implicit none

  double precision, intent(out) :: mu2

	call GetMuIR2_cll(mu2)

end subroutine get_muIR2_fortran

!-------------------------------------------------------------------------------

subroutine set_deltaIR_fortran(delta1, delta2)
	use COLLIER
	implicit none
  double precision, intent(in) :: delta1, delta2

	call SetDeltaIR_cll(delta1, delta2)

end subroutine set_deltaIR_fortran

!-------------------------------------------------------------------------------

subroutine get_deltaIR_fortran(delta1, delta2)
	use COLLIER
	implicit none

  double precision, intent(out) :: delta1, delta2

	call GetDeltaIR_cll(delta1, delta2)

end subroutine get_deltaIR_fortran

!-------------------------------------------------------------------------------

subroutine a0_fortran(res, msq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: msq

	call A0_cll(res, msq)

end subroutine a0_fortran

!-------------------------------------------------------------------------------

subroutine bget_fortran(res, i,j, p2, m1sq, m2sq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p2, m1sq, m2sq
  integer, intent(in) :: i,j
  double complex :: Bcoeff(0:1,0:2), Bcoeffuv(0:1,0:2)

	call B_cll(Bcoeff, Bcoeffuv, p2, m1sq, m2sq, 2)
	res = Bcoeff(i,j)

end subroutine bget_fortran

!-------------------------------------------------------------------------------


subroutine b0_fortran(res, p2, m1sq, m2sq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p2, m1sq, m2sq

	call B0_cll(res, p2, m1sq, m2sq)

end subroutine b0_fortran

!-------------------------------------------------------------------------------

subroutine b1_fortran(res, p2, m1sq, m2sq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p2, m1sq, m2sq
  double complex :: Bcoeff(0:1,0:2), Bcoeffuv(0:1,0:2)

	call B_cll(Bcoeff, Bcoeffuv, p2, m1sq, m2sq, 2)
	res = Bcoeff(0,1)

end subroutine b1_fortran

!-------------------------------------------------------------------------------

subroutine b00_fortran(res, p2, m1sq, m2sq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p2, m1sq, m2sq
  double complex :: Bcoeff(0:1,0:2), Bcoeffuv(0:1,0:2)

	call B_cll(Bcoeff, Bcoeffuv, p2, m1sq, m2sq, 2)
	res = Bcoeff(1,0)

end subroutine b00_fortran

!-------------------------------------------------------------------------------

subroutine b11_fortran(res, p2, m1sq, m2sq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p2, m1sq, m2sq
  double complex :: Bcoeff(0:1,0:2), Bcoeffuv(0:1,0:2)

	call B_cll(Bcoeff, Bcoeffuv, p2, m1sq, m2sq, 2)
	res = Bcoeff(0,2)

end subroutine b11_fortran
!-------------------------------------------------------------------------------

subroutine db0_fortran(res, p2, m1sq, m2sq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p2, m1sq, m2sq
  double complex :: db0res

	call DB0_cll(db0res, p2, m1sq, m2sq)
    res = db0res

end subroutine db0_fortran

!-------------------------------------------------------------------------------

subroutine db1_fortran(res, p2, m1sq, m2sq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p2, m1sq, m2sq
  double complex :: db1res

	call dB1_cll(db1res, p2, m1sq, m2sq)
	res = db1res

end subroutine db1_fortran

!-------------------------------------------------------------------------------

subroutine db00_fortran(res, p2, m1sq, m2sq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p2, m1sq, m2sq
  double complex :: db00res,db00uv

	call DB00_cll(db00res, db00uv, p2, m1sq, m2sq)
    res = db00res

end subroutine db00_fortran

!-------------------------------------------------------------------------------

subroutine db11_fortran(res, p2, m1sq, m2sq)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p2, m1sq, m2sq
  double complex :: db11res

	call DB11_cll(db11res, p2, m1sq, m2sq)
    res = db11res

end subroutine db11_fortran

!-------------------------------------------------------------------------------

subroutine cget_fortran(res, i,j,k,p10, p21, p20, m02, m12, m22)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p10, p21, p20, m02, m12, m22
  integer, intent(in) :: i,j,k
  double complex :: Ccoeff(0:2,0:2,0:2), Ccoeffuv(0:2,0:2,0:2)

	call C_cll(Ccoeff, Ccoeffuv, p10, p21, p20, m02, m12, m22, 2)
	res = Ccoeff(i,j,k)

end subroutine cget_fortran

!-------------------------------------------------------------------------------

subroutine c0_fortran(res, p10, p21, p20, m02, m12, m22)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p10, p21, p20, m02, m12, m22
  double complex :: Ccoeff(0:2,0:2,0:2), Ccoeffuv(0:2,0:2,0:2)

	call C_cll(Ccoeff, Ccoeffuv, p10, p21, p20, m02, m12, m22, 2)
	res = Ccoeff(0,0,0)

end subroutine c0_fortran

!-------------------------------------------------------------------------------

subroutine c1_fortran(res, p10, p21, p20, m02, m12, m22)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p10, p21, p20, m02, m12, m22
  double complex :: Ccoeff(0:2,0:2,0:2), Ccoeffuv(0:2,0:2,0:2)

	call C_cll(Ccoeff, Ccoeffuv, p10, p21, p20, m02, m12, m22, 2)
	res = Ccoeff(2,0,0)

end subroutine c1_fortran

!-------------------------------------------------------------------------------

subroutine c2_fortran(res, p10, p21, p20, m02, m12, m22)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p10, p21, p20, m02, m12, m22
  double complex :: Ccoeff(0:2,0:2,0:2), Ccoeffuv(0:2,0:2,0:2)

	call C_cll(Ccoeff, Ccoeffuv, p10, p21, p20, m02, m12, m22, 2)
	res = Ccoeff(0,2,0)

end subroutine c2_fortran

!-------------------------------------------------------------------------------

subroutine c00_fortran(res, p10, p21, p20, m02, m12, m22)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p10, p21, p20, m02, m12, m22
  double complex :: Ccoeff(0:2,0:2,0:2), Ccoeffuv(0:2,0:2,0:2)

	call C_cll(Ccoeff, Ccoeffuv, p10, p21, p20, m02, m12, m22, 2)
	res = Ccoeff(1,0,0)

end subroutine c00_fortran

!-------------------------------------------------------------------------------

subroutine c11_fortran(res, p10, p21, p20, m02, m12, m22)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p10, p21, p20, m02, m12, m22
  double complex :: Ccoeff(0:2,0:2,0:2), Ccoeffuv(0:2,0:2,0:2)

	call C_cll(Ccoeff, Ccoeffuv, p10, p21, p20, m02, m12, m22, 2)
	res = Ccoeff(1,1,0)

end subroutine c11_fortran

!-------------------------------------------------------------------------------

subroutine c22_fortran(res, p10, p21, p20, m02, m12, m22)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
  double complex, intent(in) :: p10, p21, p20, m02, m12, m22
  double complex :: Ccoeff(0:2,0:2,0:2), Ccoeffuv(0:2,0:2,0:2)

	call C_cll(Ccoeff, Ccoeffuv, p10, p21, p20, m02, m12, m22, 2)
	res = Ccoeff(0,1,1)

end subroutine c22_fortran

!-------------------------------------------------------------------------------

subroutine dget_fortran(res, i, j, k, l, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
    integer, intent(in) :: i,j,k,l
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(i,j,k,l)

end subroutine dget_fortran

!-------------------------------------------------------------------------------

subroutine d0_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32

	call D0_cll(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)

end subroutine d0_fortran

!-------------------------------------------------------------------------------

subroutine d1_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none

	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,0,0)

end subroutine d1_fortran

!-------------------------------------------------------------------------------

subroutine d2_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,1,0)
	
end subroutine d2_fortran

!-------------------------------------------------------------------------------

subroutine d3_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,0,1)
	
end subroutine d3_fortran

!-------------------------------------------------------------------------------

subroutine d00_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,0,0,0)
	
end subroutine d00_fortran

!-------------------------------------------------------------------------------

subroutine d11_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,2,0,0)
	
end subroutine d11_fortran

!-------------------------------------------------------------------------------

subroutine d12_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,1,0)
	
end subroutine d12_fortran

!-------------------------------------------------------------------------------

subroutine d13_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,0,1)
	
end subroutine d13_fortran

!-------------------------------------------------------------------------------

subroutine d22_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,2,0)
	
end subroutine d22_fortran

!-------------------------------------------------------------------------------

subroutine d23_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,1,1)
	
end subroutine d23_fortran

!-------------------------------------------------------------------------------

subroutine d33_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,0,2)
	
end subroutine d33_fortran

!-------------------------------------------------------------------------------

subroutine d001_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,1,0,0)
	
end subroutine d001_fortran

!-------------------------------------------------------------------------------

subroutine d002_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,0,1,0)
	
end subroutine d002_fortran

!-------------------------------------------------------------------------------

subroutine d003_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,0,0,1)
	
end subroutine d003_fortran

!-------------------------------------------------------------------------------

subroutine d111_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,3,0,0)
	
end subroutine d111_fortran

!-------------------------------------------------------------------------------

subroutine d112_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,2,1,0)
	
end subroutine d112_fortran

!-------------------------------------------------------------------------------

subroutine d113_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,2,0,1)
	
end subroutine d113_fortran

!-------------------------------------------------------------------------------

subroutine d122_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,2,0)
	
end subroutine d122_fortran

!-------------------------------------------------------------------------------

subroutine d123_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,1,1)
	
end subroutine d123_fortran

!-------------------------------------------------------------------------------

subroutine d133_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,0,2)
	
end subroutine d133_fortran

!-------------------------------------------------------------------------------

subroutine d222_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,3,0)
	
end subroutine d222_fortran

!-------------------------------------------------------------------------------

subroutine d223_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,2,1)
	
end subroutine d223_fortran

!-------------------------------------------------------------------------------

subroutine d233_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,1,2)
	
end subroutine d233_fortran

!-------------------------------------------------------------------------------

subroutine d333_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,0,3)
	
end subroutine d333_fortran

!-------------------------------------------------------------------------------

subroutine d0000_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(2,0,0,0)
	
end subroutine d0000_fortran

!-------------------------------------------------------------------------------

subroutine d0011_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,2,0,0)
	
end subroutine d0011_fortran

!-------------------------------------------------------------------------------

subroutine d0012_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,1,1,0)
	
end subroutine d0012_fortran

!-------------------------------------------------------------------------------

subroutine d0013_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,1,0,1)
	
end subroutine d0013_fortran

!-------------------------------------------------------------------------------

subroutine d0022_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,0,2,0)
	
end subroutine d0022_fortran

!-------------------------------------------------------------------------------

subroutine d0023_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,0,1,1)
	
end subroutine d0023_fortran

!-------------------------------------------------------------------------------

subroutine d0033_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(1,0,0,2)
	
end subroutine d0033_fortran

!-------------------------------------------------------------------------------

subroutine d1111_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,4,0,0)
	
end subroutine d1111_fortran

!-------------------------------------------------------------------------------

subroutine d1112_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,3,1,0)
	
end subroutine d1112_fortran

!-------------------------------------------------------------------------------

subroutine d1113_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,3,0,1)
	
end subroutine d1113_fortran

!-------------------------------------------------------------------------------

subroutine d1122_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,2,2,0)
	
end subroutine d1122_fortran

!-------------------------------------------------------------------------------

subroutine d1123_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,2,1,1)
	
end subroutine d1123_fortran

!-------------------------------------------------------------------------------

subroutine d1133_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,2,0,2)
	
end subroutine d1133_fortran

!-------------------------------------------------------------------------------

subroutine d1222_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,3,0)
	
end subroutine d1222_fortran

!-------------------------------------------------------------------------------

subroutine d1223_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,2,1)
	
end subroutine d1223_fortran

!-------------------------------------------------------------------------------

subroutine d1233_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,1,2)
	
end subroutine d1233_fortran

!-------------------------------------------------------------------------------

subroutine d1333_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,1,0,3)
	
end subroutine d1333_fortran

!-------------------------------------------------------------------------------

subroutine d2222_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,4,0)
	
end subroutine d2222_fortran

!-------------------------------------------------------------------------------

subroutine d2223_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,3,1)
	
end subroutine d2223_fortran

!-------------------------------------------------------------------------------

subroutine d2233_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,2,2)
	
end subroutine d2233_fortran

!-------------------------------------------------------------------------------

subroutine d2333_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,1,3)
	
end subroutine d2333_fortran

!-------------------------------------------------------------------------------

subroutine d3333_fortran(res, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32)
	use COLLIER
	implicit none
	
	double complex, intent(out) :: res
	double complex, intent(in) :: p10, p21, p32, p30, p20, p31, m02, m12, m22, m32
	double complex :: Dcoeff(0:2,0:4,0:4,0:4), Dcoeffuv(0:2,0:4,0:4,0:4)
	
	call D_cll(Dcoeff, Dcoeffuv, p10, p21, p32, p30, p20, p31, m02, m12, m22, m32, 4)
	res = Dcoeff(0,0,0,4)
	
end subroutine d3333_fortran

!-------------------------------------------------------------------------------
