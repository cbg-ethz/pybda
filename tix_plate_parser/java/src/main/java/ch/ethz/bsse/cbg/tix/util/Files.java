package ch.ethz.bsse.cbg.tix.util;

import org.apache.commons.io.FileUtils;

import java.io.File;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

/**
 * @author Simon Dirmeier {@literal simon.dirmeier@gmx.de}
 */
public class Files
{
    private Files() {}

    @SuppressWarnings("unchecked")
    public static List<File> listFiles(File dir)
    {
        return (List<File>) FileUtils.listFiles(dir, null, true).stream().collect(Collectors.toList());
    }
}
