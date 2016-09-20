package ch.ethz.bsse.cbg.tix.structs;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;

/**
 * @author Simon Dirmeier {@literal simon.dirmeier@gmx.de}
 */
public class CellFeature
{
    private static final Logger _LOGGER = LoggerFactory.getLogger(CellFeature.class);
    private double[][] features;

    public CellFeature(File file)
    {
        features = parse(file);
    }

    private static double[][] parse(File file)
    {
        BufferedReader bR;
        try
        {
            bR = new BufferedReader(new FileReader(file));
            // TODO
            // HERE PARSE MATLAB
            bR.close();
        }
        catch (IOException e)
        {
            _LOGGER.error("Could not find file {}", file.getAbsoluteFile());
            System.exit(-1);
        }
        // TODO: better change that
        return new double[10][10];
    }

    @Override
    public String toString()
    {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < features.length; i++)
        {
            if (i == 5)
                break;
            for (int j = 0; j < features[i].length; j++)
            {
                if (j >= 5)
                    break;
                sb.append(features[i][j]);
                if (j < 4 && j < features[i].length - 1)
                    sb.append(", ");
            }
            sb.append("\n");
        }
        return sb.toString();
    }
}
