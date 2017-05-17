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


import ncsa.hdf.hdf5lib.H5;
import ncsa.hdf.hdf5lib.HDF5Constants;

/**
 * @author Simon Dirmeier {@literal simon.dirmeier@bsse.ethz.ch}
 */
public final class Main
{

    static final String FILENAME = "~/Desktop/H5_CreateFile.h5";

    public static void main(String[] args)
    {
        Main.createFile();
    }

    private static void createFile()
    {
        int file_id = -1;

        // Create a new file using default properties.
        try
        {
            file_id = H5.H5Fcreate(FILENAME,
                                   HDF5Constants.H5F_ACC_TRUNC,
                                   HDF5Constants.H5P_DEFAULT,
                                   HDF5Constants.H5P_DEFAULT);
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }

        // Close the file.
        try
        {
            if (file_id >= 0)
                H5.H5Fclose(file_id);
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }

    }

}
