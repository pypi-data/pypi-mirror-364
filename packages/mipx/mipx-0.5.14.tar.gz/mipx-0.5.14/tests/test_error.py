
import mipx


if __name__ == "__main__":
    model = mipx.Model("SCIP")
    x = model.addVar(lb=1, ub=10, name='x')
    y = model.addVar(lb=1, ub=10, name='y')
    # model.setObjective(10)
    model.setObjectiveN(10*x, index=0, weight=10)
    model.setObjectiveN(10*x, index=1, weight=10)
    model.setObjectiveN(10*y, index=3, weight=1)
    model.setObjectiveN(x, index=2, weight=1)
    model.setObjectiveN(100, index=4, weight=1)
    model.setObjectiveN(100, index=4, weight=1)
    # model.setObjective(10*x + 10*y)
    status = model.optimize(mipx.MAXIMIZE)
    if status == mipx.OPTIMAL:
        print("Optimal solution found")
        print("Obj value:", model.ObjVal)
        mipx.debugVar(x)
        mipx.debugVar(y)
        model.reportMultiObjValue()
    else:
        print("No solution found")
