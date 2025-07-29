from .collierf2py import *


def initialize() -> None:
    """
    Initalizes pyCollier.
    """
    initialize_fortran()


def set_renscale(mu2: float) -> None:
    """
    Sets the squared renormalization scale.

    Args:
        mu2: square of renormalization scale
    """
    set_renscale_fortran(mu2)


def get_renscale() -> float:
    """
    Returns:
        the squared renormalization scale
    """
    return get_renscale_fortran()

def set_delta(delta: float) -> None:
    """
    Sets UV regulator.

    Args:
        delta: UV regulator
    """
    set_delta_fortran(delta)


def get_delta() -> float:
    """
    Returns:
        the UV regulator
    """
    return get_delta_fortran()

def set_muIR2(mu2: float) -> None:
    """
    Sets the squared IR scale.

    Args:
        mu2: square of IR scale
    """
    set_muir2_fortran(mu2)


def get_muIR2() -> float:
    """
    Returns:
        the squared IR scale
    """
    return get_muir2_fortran()

def set_deltaIR(delta1: float, delta2: float) -> None:
    """
    Sets UV regulator.

    Args:
        delta: UV regulator
    """
    set_deltair_fortran(delta1, delta2)


def get_deltaIR() -> tuple:
    """
    Returns:
        the IR regulators
    """
    return get_deltair_fortran()

def a0(msq: complex) -> complex:
    """
    The scalar 1-point loop integral $A_0(m^2)$.

    Args:
        msq: mass squared
    Returns:
        the value of the loop integral
    """
    return a0_fortran(msq)


def bget(n0: int, n1: int, psq: complex, m1sq: complex, m2sq: complex) -> complex:
    r"""
    The scalar 2-point loop integral $B_{\underbrace{0..0}_{n_0}\underbrace{1..1}_{n_1}}(p^2, m_1^2, m_2^2)$.

    Args:
        n0: number of $0$ tensor coefficients
        n1: number of $1$ tensor coefficients
        psq: inflowing squared momentum
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return bget_fortran(n0, n1, psq, m1sq, m2sq)


def b0(psq: complex, m1sq: complex, m2sq: complex) -> complex:
    r"""
    The scalar 2-point loop integral $B_0(p^2, m_1^2, m_2^2)$.

    Args:
        psq: inflowing squared momentum
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return b0_fortran(psq, m1sq, m2sq)


def b1(psq: complex, m1sq: complex, m2sq: complex) -> complex:
    r"""
    The scalar 2-point loop integral $B_1(p^2, m_1^2, m_2^2)$.

    Args:
        psq: inflowing squared momentum
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return b1_fortran(psq, m1sq, m2sq)


def b00(psq: complex, m1sq: complex, m2sq: complex) -> complex:
    r"""
    The scalar 2-point loop integral $B_{00}(p^2, m_1^2, m_2^2)$.

    Args:
        psq: inflowing squared momentum
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return b00_fortran(psq, m1sq, m2sq)


def b11(psq: complex, m1sq: complex, m2sq: complex) -> complex:
    r"""
    The scalar 2-point loop integral $B_{11}(p^2, m_1^2, m_2^2)$.

    Args:
        psq: inflowing squared momentum
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return b11_fortran(psq, m1sq, m2sq)


def db0(psq: complex, m1sq: complex, m2sq: complex) -> complex:
    r"""
    The momentum-derivative of the scalar 2-point loop integral $B_0$: 
    $B_{0}^\prime(p^2, m_1^2, m_2^2)$.

    Args:
        psq: inflowing squared momentum
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return db0_fortran(psq, m1sq, m2sq)


def db1(psq: complex, m1sq: complex, m2sq: complex) -> complex:
    r"""
    The momentum-derivative of the scalar 2-point loop integral $B_{1}$: 
    $B_{1}^\prime(p^2, m_1^2, m_2^2)$.

    Args:
        psq: inflowing squared momentum
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return db1_fortran(psq, m1sq, m2sq)


def db00(psq: complex, m1sq: complex, m2sq: complex) -> complex:
    r"""
    The momentum-derivative of the scalar 2-point loop integral $B_{00}$: 
    $B_{00}^\prime(p^2, m_1^2, m_2^2)$.

    Args:
        psq: inflowing squared momentum
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return db00_fortran(psq, m1sq, m2sq)


def db11(psq: complex, m1sq: complex, m2sq: complex) -> complex:
    r"""
    The momentum-derivative of the scalar 2-point loop integral $B_{11}$: 
    $B_{11}^\prime(p^2, m_1^2, m_2^2)$.

    Args:
        psq: inflowing squared momentum
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return db11_fortran(psq, m1sq, m2sq)


def cget(n0: int, n1: int, n2: int, p1sq: complex, p2sq: complex, p12: complex, m1sq: complex, m2sq: complex, m3sq: complex) -> complex:
    r"""
    The scalar 3-point loop integral $C_{\underbrace{0..0}_{n_0}\underbrace{1..1}_{n_1}\underbrace{2..2}_{n_2}}(p_1^2, p_2^2, (p_1 + p_2)^2, m_1^2, m_2^2, m_3^2)$.

    Args:
        n0: number of $0$ tensor coefficients
        n1: number of $1$ tensor coefficients
        n2: number of $2$ tensor coefficients
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
    Returns:
        the value of the loop integral
    """
    return cget_fortran(n0, n1, n2, p1sq, p2sq, p12, m1sq, m2sq, m3sq)


def c0(p1sq: complex, p2sq: complex, p12: complex, m1sq: complex, m2sq: complex, m3sq: complex) -> complex:
    r"""
    The scalar 3-point loop integral $C_{0}(p_1^2, p_2^2, (p_1 + p_2)^2, m_1^2, m_2^2, m_3^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
    Returns:
        the value of the loop integral
    """
    return c0_fortran(p1sq, p2sq, p12, m1sq, m2sq, m3sq)


def c1(p1sq: complex, p2sq: complex, p12: complex, m1sq: complex, m2sq: complex, m3sq: complex) -> complex:
    r"""
    The scalar 3-point loop integral $C_{1}(p_1^2, p_2^2, (p_1 + p_2)^2, m_1^2, m_2^2, m_3^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
    Returns:
        the value of the loop integral
    """
    return c1_fortran(p1sq, p2sq, p12, m1sq, m2sq, m3sq)


def c2(p1sq: complex, p2sq: complex, p12: complex, m1sq: complex, m2sq: complex, m3sq: complex) -> complex:
    r"""
    The scalar 3-point loop integral $C_{2}(p_1^2, p_2^2, (p_1 + p_2)^2, m_1^2, m_2^2, m_3^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
    Returns:
        the value of the loop integral
    """
    return c2_fortran(p1sq, p2sq, p12, m1sq, m2sq, m3sq)


def c00(p1sq: complex, p2sq: complex, p12: complex, m1sq: complex, m2sq: complex, m3sq: complex) -> complex:
    r"""
    The scalar 3-point loop integral $C_{00}(p_1^2, p_2^2, (p_1 + p_2)^2, m_1^2, m_2^2, m_3^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
    Returns:
        the value of the loop integral
    """
    return c00_fortran(p1sq, p2sq, p12, m1sq, m2sq, m3sq)


def c11(p1sq: complex, p2sq: complex, p12: complex, m1sq: complex, m2sq: complex, m3sq: complex) -> complex:
    r"""
    The scalar 3-point loop integral $C_{11}(p_1^2, p_2^2, (p_1 + p_2)^2, m_1^2, m_2^2, m_3^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
    Returns:
        the value of the loop integral
    """
    return c11_fortran(p1sq, p2sq, p12, m1sq, m2sq, m3sq)


def c22(p1sq: complex, p2sq: complex, p12: complex, m1sq: complex, m2sq: complex, m3sq: complex) -> complex:
    r"""
    The scalar 3-point loop integral $C_{22}(p_1^2, p_2^2, (p_1 + p_2)^2, m_1^2, m_2^2, m_3^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
    Returns:
        the value of the loop integral
    """
    return c22_fortran(p1sq, p2sq, p12, m1sq, m2sq, m3sq)


def dget(n0: int, n1: int, n2: int, n3: int, p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{\underbrace{0..0}_{n_0}\underbrace{1..1}_{n_1}\underbrace{2..2}_{n_2}\underbrace{3..3}_{n_3}}(p_1^2, p_2^2, (p_1 + p_2)^2, m_1^2, m_2^2, m_3^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return dget_fortran(n0, n1, n2, n3, p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d0(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{0}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d0_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d2(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{2}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d2_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d3(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{3}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d3_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d00(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{00}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d00_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d11(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{11}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d11_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d12(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{12}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d12_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d13(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{13}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d13_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d22(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{22}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d22_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d23(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{23}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d23_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d33(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{33}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d33_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d001(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{001}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d001_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d002(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{002}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d002_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d003(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{003}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d003_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d111(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{111}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d111_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d112(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{112}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d112_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d113(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{113}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d113_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d122(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{122}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d122_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d123(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{123}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d123_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d133(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{133}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d133_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d222(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{222}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d222_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d223(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{223}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d223_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d233(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{233}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d233_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d333(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{333}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d333_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d0000(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{0000}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d0000_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d0011(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{0011}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d0011_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d0012(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{0012}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d0012_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d0013(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{0013}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d0013_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d0022(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{0022}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d0022_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d0023(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{0023}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d0023_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d0033(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{0033}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d0033_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1111(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1111}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1111_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1112(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1112}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1112_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1113(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1113}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1113_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1122(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1122}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1122_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1123(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1123}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1123_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1222(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1222}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1222_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1223(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1223}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1223_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1233(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1233}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1233_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d1333(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{1333}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d1333_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d2222(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{2222}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d2222_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d2223(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{2223}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d2223_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d2233(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{2233}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d2233_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d2333(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{2333}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d2333_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)


def d3333(p1sq: complex, p2sq: complex, p3sq: complex, p4sq: complex, p12: complex, p23: complex, m1sq: complex, m2sq: complex, m3sq: complex, m4sq: complex) -> complex:
    r"""
    The scalar 4-point loop integral $D_{3333}(p_1^2, p_2^2, p_3^2, p_4^2, (p_1 + p_2)^2, (p_2 + p_3)^2, m_1^2, m_2^2, m_3^2, m_4^2)$.

    Args:
        p1sq: square of the 1st inflowing momentum
        p2sq: square of the 2nd inflowing momentum
        p3sq: square of the 3rd inflowing momentum
        p4sq: square of the 4th inflowing momentum
        p12: square of difference between 1st and 2nd inflowing momenta
        p34: square of difference between 2nd and 3rd inflowing momenta
        msq1: first mass squared
        msq2: second mass squared
        msq3: third mass squared
        msq4: fourth mass squared
    Returns:
        the value of the loop integral
    """
    return d3333_fortran(p1sq, p2sq, p3sq, p4sq, p12, p23, m1sq, m2sq, m3sq, m4sq)
