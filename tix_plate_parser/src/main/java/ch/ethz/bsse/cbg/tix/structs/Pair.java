package ch.ethz.bsse.cbg.tix.structs;

/**
 * @author Simon Dirmeier {@literal simon.dirmeier@gmx.de}
 */
public final class Pair<T extends Comparable<T>, U> implements Comparable<Pair<T, U>>
{
    private final T _T;
    private final U _U;

    public Pair(T t, U u)
    {
        this._T = t;
        this._U = u;
    }

    public T first()
    {
        return this._T;
    }

    public U second()
    {
        return this._U;
    }

    @Override
    public int compareTo(Pair<T, U> o)
    {
        return o._T.compareTo(o._T);
    }
}
