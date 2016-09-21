package ch.ethz.bsse.cbg.tix.structs;

import de.unknownreality.dataframe.DataFrame;
import de.unknownreality.dataframe.column.StringColumn;
import de.unknownreality.dataframe.csv.CSVReader;
import de.unknownreality.dataframe.csv.CSVReaderBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;

/**
 * @author Simon Dirmeier {@literal simon.dirmeier@gmx.de}
 */
public final class LibraryLayout
{
    private final static Logger _LOGGER = LoggerFactory.getLogger(LibraryLayout.class);
    private final File _META_FILE;
    private String[] _header;
    private final DataFrame _TABLE;

    private LibraryLayout(File file)
    {
        this._META_FILE = file;
        CSVReader reader = CSVReaderBuilder.create()
                                           .containsHeader(true)
                                           .withSeparator('\t')
                                           .withHeaderPrefix("")
                                           .load(file);
        this._TABLE = reader.toDataFrame()
                            .addColumn(new StringColumn("Barcode"))
                            .addColumn(new StringColumn("Group"))
                            .addColumn(new StringColumn("Group"))
                            .build();


        parse();
    }

    public static LibraryLayout instance(String file)
    {
        return new LibraryLayout(new File(file));
    }

    private void parse()
    {
        BufferedReader bR;
        try
        {
            bR = new BufferedReader(new FileReader(this._META_FILE));
            String line = bR.readLine();
            this._header = line.split("\t");
            while ((line = bR.readLine()) != null)
            {
                if (line.startsWith(this._header[0])) continue;
                String toks[] = line.split("\t");
            }
            bR.close();
        }
        catch (IOException e)
        {
            _LOGGER.error("Could not open file {}", this._META_FILE.getAbsoluteFile());
            System.exit(-1);
        }
    }
}
