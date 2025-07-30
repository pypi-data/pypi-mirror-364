from pyfreefem import FreeFemRunner
from nullspace_optimizer import undecorate, bound_constraints_optimizable,\
    memoize, nlspace_solve
import nullspace_optimizer.examples.topopt_examples.ex07_heat_nlspace as ex07   
import matplotlib.pyplot as plt
    

Heat_TO_original = undecorate(ex07.Heat_TO)
solveMP0P0 = ex07.solveMP0P0    
MP1P0 = ex07.MP1P0
    
@bound_constraints_optimizable(l=0, u=1)
class Heat_TO(Heat_TO_original):
    @memoize(func_name="dJ", debug=2)
    def dJ(self,rho):   
        return super().dJ(rho)
        
    @memoize(func_name="dH", debug=2)
    def dH(self, rho):  
        return super().dH(rho)

    def dJT(self, rho): 
        dJT = solveMP0P0(MP1P0.T @ ex07.solveA(MP1P0 @ solveMP0P0(self.dJ(rho))))
        return dJT
        
    def dHT(self, rho): 
        dHT = solveMP0P0(MP1P0.T @ ex07.solveA(MP1P0 @ solveMP0P0(self.dH(rho))))
        return dHT
        
    # Normally ignored
    def inner_product(self, rho):   
        return None

if __name__ == "__main__":
    ex07.init(100)
    plt.ion()

    case = Heat_TO(plot=True)
    params = dict(dt=0.3, itnormalisation=50, maxit=150,
                  save_only_N_iterations=1,
                  save_only_Q_constraints=5,
                  qp_solver='qpalm',
                  tol_qp=1e-8)
    nlspace_solve(case, params)
