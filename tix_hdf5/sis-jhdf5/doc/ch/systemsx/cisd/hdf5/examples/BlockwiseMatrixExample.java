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

import java.util.Random;

import org.apache.commons.lang.ArrayUtils;

import ch.systemsx.cisd.base.mdarray.MDIntArray;
import ch.systemsx.cisd.hdf5.HDF5Factory;
import ch.systemsx.cisd.hdf5.HDF5MDDataBlock;
import ch.systemsx.cisd.hdf5.IHDF5Reader;
import ch.systemsx.cisd.hdf5.IHDF5Writer;

/**
 * An example for block-wise reading and writing of an integer matrix. This can be used to read and
 * write arrays and matrices that are too big to fit into memory. Only the block
 */
public class BlockwiseMatrixExample
{

    public static void main(String[] args)
    {
        Random rng = new Random();
        int[][] mydata = new int[10][10];

        // Write the integer matrix.
        IHDF5Writer writer = HDF5Factory.open("largeimatrix.h5");
        // Define the block size as 10 x 10.
        writer.int32().createMatrix("mydata", 10, 10);
        // Write 5 x 7 blocks.
        for (int bx = 0; bx < 5; ++bx)
        {
            for (int by = 0; by < 7; ++by)
            {
                fillMatrix(rng, mydata);
                writer.int32().writeMatrixBlock("mydata", mydata, bx, by);
            }
        }
        writer.close();

        // Read the matrix in again, using the "natural" 10 x 10 blocks.
        IHDF5Reader reader = HDF5Factory.openForReading("largeimatrix.h5");
        for (HDF5MDDataBlock<MDIntArray> block : reader.int32().getMDArrayNaturalBlocks("mydata"))
        {
            System.out.println(ArrayUtils.toString(block.getIndex()) + " -> "
                    + block.getData().toString());
        }

        // Read a 1d sliced block of size 10 where the first index is fixed
        System.out.println(reader.int32().readSlicedMDArrayBlock("mydata", new int[]
            { 10 }, new long[]
            { 4 }, new long[]
            { 30, -1 }));

        reader.close();
    }

    static void fillMatrix(Random rng, int[][] mydata)
    {
        for (int i = 0; i < mydata.length; ++i)
        {
            for (int j = 0; j < mydata[i].length; ++j)
            {
                mydata[i][j] = rng.nextInt();
            }
        }
    }

}
