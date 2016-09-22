package ch.ethz.bsse.cbg.tix.structs;

import com.jmatio.io.MatFileReader;
import com.jmatio.types.MLArray;
import com.jmatio.types.MLStructure;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.util.Collection;
import java.util.Map;

/**
 * @author Simon Dirmeier {@literal simon.dirmeier@gmx.de}
 */
public class CellFeature
{
    private static final Logger _LOGGER = LoggerFactory.getLogger(CellFeature.class);
    private double[][] _features;

    public CellFeature(File file)
    {
        _features = parse(file);
    }

    private double[][] parse(File file)
    {
        System.out.println(6);
        MatFileReader reader;
        try
        {
            reader = new MatFileReader(file);
            MLStructure cont = (MLStructure) reader.getContent().get("handles");
            if (cont.isStruct())
            {
                MLArray arr = cont.getField("handles");
                System.out.println(arr);
            }

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
        for (int i = 0; i < _features.length; i++)
        {
            if (i == 5)
                break;
            for (int j = 0; j < _features[i].length; j++)
            {
                if (j >= 5)
                    break;
                sb.append(_features[i][j]);
                if (j < 4 && j < _features[i].length - 1)
                    sb.append(", ");
            }
            sb.append("\n");
        }
        return sb.toString();
    }
}
