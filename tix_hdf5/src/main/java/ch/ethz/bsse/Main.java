/**
 * tix_hdf5: HDF5 file IO for RNAi screens
 * <p>
 * Copyright (C) Simon Dirmeier
 * <p>
 * This file is part of tix_hdf5.
 * <p>
 * tix_hdf5 is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * <p>
 * tix_hdf5 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * <p>
 * You should have received a copy of the GNU General Public License
 * along with tix_hdf5. If not, see <http://www.gnu.org/licenses/>.
 */


package ch.ethz.bsse;


import ch.systemsx.cisd.hdf5.HDF5Factory;
import ch.systemsx.cisd.hdf5.IHDF5SimpleWriter;
import ch.systemsx.cisd.hdf5.IHDF5Writer;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * @author Simon Dirmeier {@literal simon.dirmeier@bsse.ethz.ch}
 */
public final class Main
{
    public static void main(String[] args) throws IOException
    {
        float[] mydata = new float[100000];
        IHDF5Writer writer = HDF5Factory.open("/Users/simondi/Desktop/bla.h5");

        Path p = Paths.get("/Users/simondi/Desktop/bla.tsv");
        try (BufferedWriter bW = Files.newBufferedWriter(p))
        {
            for (int i = 0; i < 10000; i++)
            {
                writer.writeFloatArray("mydata" + String.valueOf(i), mydata);
                for (float aMydata : mydata)
                {
                    bW.write(aMydata + " ");
                }
                bW.write("\n");
            }
        }

        writer.close();



    }
}
