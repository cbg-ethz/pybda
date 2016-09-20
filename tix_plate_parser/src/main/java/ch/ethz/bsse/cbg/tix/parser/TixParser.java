package ch.ethz.bsse.cbg.tix.parser;

import ch.ethz.bsse.cbg.tix.structs.CellFeature;
import ch.ethz.bsse.cbg.tix.util.Files;

import java.io.File;
import java.util.List;

/**
 * @author Simon Dirmeier {@literal simon.dirmeier@gmx.de}
 */
public final class TixParser
{
    private final String _PLATE_FOLDER;
    private final String _META_FILE;

    public TixParser(String plateFolder, String metaFile)
    {
        this._PLATE_FOLDER = plateFolder;
        this._META_FILE = metaFile;
    }

    public final void parser()
    {
        List<File> fileList = Files.listFiles(new File(_PLATE_FOLDER));
        final int sz = fileList.size();
        CellFeature[] plateFeatures = new CellFeature[sz];
        for (int i = 0; i < sz; i++)
        {
            plateFeatures[i] = new CellFeature(fileList.get(i));
            System.out.println(plateFeatures[i]);
        }
    }
}
