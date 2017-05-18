/*
 * Copyright 2011 ETH Zuerich, CISD
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ch.systemsx.cisd.hdf5.examples;

import org.apache.commons.lang.ArrayUtils;

import ch.systemsx.cisd.hdf5.HDF5Factory;
import ch.systemsx.cisd.hdf5.IHDF5SimpleReader;
import ch.systemsx.cisd.hdf5.IHDF5SimpleWriter;

/**
 * A simple example for writing and reading a float array.
 */
public class FloatArrayExample
{
    public static void main(String[] args)
    {
        float[] mydata = new float[10];
        for (int i = 0; i < mydata.length; ++i)
        {
            mydata[i] = (float) Math.sqrt(i);
        }

        // Write a float array
        IHDF5SimpleWriter writer = HDF5Factory.open("farray.h5");
        writer.writeFloatArray("mydata", mydata);
        writer.close();

        // Read a float array
        IHDF5SimpleReader reader = HDF5Factory.openForReading("farray.h5");
        System.out.println(ArrayUtils.toString(reader.readFloatArray("mydata")));
        reader.close();
    }
}
