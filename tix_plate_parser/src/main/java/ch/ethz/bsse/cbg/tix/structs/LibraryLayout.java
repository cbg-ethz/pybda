package ch.ethz.bsse.cbg.tix.structs;

import de.unknownreality.dataframe.DataFrame;
import de.unknownreality.dataframe.DataRow;
import de.unknownreality.dataframe.column.IntegerColumn;
import de.unknownreality.dataframe.column.StringColumn;
import de.unknownreality.dataframe.csv.CSVReader;
import de.unknownreality.dataframe.csv.CSVReaderBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

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
                            .addColumn(new StringColumn("barcode"))
                            .addColumn(new StringColumn("pathogen"))
                            .addColumn(new StringColumn("geneset"))
                            .addColumn(new IntegerColumn("replicate"))
                            .addColumn(new StringColumn("library"))
                            .addColumn(new StringColumn("row"))
                            .addColumn(new IntegerColumn("col"))
                            .addColumn(new StringColumn("well"))
                            .addColumn(new StringColumn("welltype"))
                            .addColumn(new StringColumn("genesymbol"))
                            .addColumn(new StringColumn("sirna"))
                            .build();
        this._TABLE.addIndex("idx", "barcode", "pathogen", "replicate", "library", "well");
        parse();
    }

    public static LibraryLayout instance(String file)
    {
        return new LibraryLayout(new File(file));
    }

    /**
     * Getter for a data-row given a index and search terms.
     *
     * @param barcode the plate id
     * @param pathogen the pathogen
     * @param replicate the replicate
     * @param library the library
     * @param well the well
     *
     * @return returns the sirna id
     */
    public DataRow find(String barcode, String pathogen,
                                 int replicate, String library, String well)
    {
        return this._TABLE.findByIndex("idx", barcode, pathogen, replicate, library, well);
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
