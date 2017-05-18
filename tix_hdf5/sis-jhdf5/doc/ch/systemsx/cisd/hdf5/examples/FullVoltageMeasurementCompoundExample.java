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

import java.util.Arrays;
import java.util.Date;
import java.util.List;

import org.apache.commons.lang.ArrayUtils;

import ch.systemsx.cisd.hdf5.CompoundElement;
import ch.systemsx.cisd.hdf5.HDF5CompoundDataList;
import ch.systemsx.cisd.hdf5.HDF5CompoundDataMap;
import ch.systemsx.cisd.hdf5.HDF5CompoundType;
import ch.systemsx.cisd.hdf5.HDF5Factory;
import ch.systemsx.cisd.hdf5.IHDF5Reader;
import ch.systemsx.cisd.hdf5.IHDF5Writer;

/**
 * This is a more advanced example which demonstrates reading and writing of a "compound" data set
 * that stores a temperature / voltage measurement point.
 */
public class FullVoltageMeasurementCompoundExample
{

    /**
     * A Data Transfer Object for a combined temperature / voltage measurement.
     */
    static class Measurement
    {
        private Date date;

        // Include the unit in the member name
        @CompoundElement(memberName = "temperatureInDegreeCelsius")
        private float temperature;

        // Include the unit in the member name
        @CompoundElement(memberName = "voltageInMilliVolts")
        private double voltage;

        // Mark this to be a variable-length string
        @CompoundElement(variableLength = true)
        private String comment;

        // Important: needs to have a default constructor, otherwise JHDF5 will bail out on reading.
        Measurement()
        {
        }

        Measurement(Date date, float temperatureInDegreeCelsius, double voltageInMilliVolts,
                String comment)
        {
            this.date = date;
            this.temperature = temperatureInDegreeCelsius;
            this.voltage = voltageInMilliVolts;
            this.comment = comment;
        }

        Date getDate()
        {
            return date;
        }

        void setDate(Date date)
        {
            this.date = date;
        }

        float getTemperature()
        {
            return temperature;
        }

        void setTemperature(float temperatureInDegreeCelsius)
        {
            this.temperature = temperatureInDegreeCelsius;
        }

        double getVoltage()
        {
            return voltage;
        }

        void setVoltage(double voltageInMilliVolts)
        {
            this.voltage = voltageInMilliVolts;
        }

        @Override
        public String toString()
        {
            return "Measurement [date=" + date + ", temperature=" + temperature + ", voltage="
                    + voltage + ", comment='" + comment + "']";
        }

    }

    private final IHDF5Writer hdf5Writer;

    private final IHDF5Reader hdf5Reader;

    FullVoltageMeasurementCompoundExample(String fileName, boolean readOnly)
    {
        if (readOnly)
        {
            this.hdf5Reader = HDF5Factory.openForReading(fileName);
            this.hdf5Writer = null;
        } else
        {
            this.hdf5Writer = HDF5Factory.open(fileName);
            this.hdf5Reader = hdf5Writer;
        }
    }

    void close()
    {
        hdf5Reader.close();
    }

    /**
     * Writes a new measurement to <var>datasetName</var>.
     * 
     * @param datasetName The name of the data set to write to.
     * @param measurementDate The date when the measurement was performed.
     * @param measuredTemperature The measured temperature (in degree Celsius).
     * @param measuredVoltage The measured voltage (in milli Volts).
     * @param comment A comment on the measurement.
     */
    void writeMeasurement(String datasetName, Date measurementDate, float measuredTemperature,
            double measuredVoltage, String comment)
    {
        hdf5Writer.compound().write(datasetName,
                new Measurement(measurementDate, measuredTemperature, measuredVoltage, comment));
    }

    /**
     * Writes a new measurement to <var>datasetName</var> as a map.
     * 
     * @param datasetName The name of the data set to write to.
     * @param measurementDate The date when the measurement was performed.
     * @param measuredTemperature The measured temperature (in degree Celsius).
     * @param measuredVoltage The measured voltage (in milli Volts).
     * @param comment A comment on the measurement.
     */
    void writeMeasurementAsMap(String datasetName, Date measurementDate, float measuredTemperature,
            double measuredVoltage, String comment)
    {
        HDF5CompoundDataMap map = new HDF5CompoundDataMap();
        map.put("date", measurementDate);
        map.put("temperatureInDegreeCelsius", measuredTemperature);
        map.put("voltageInMilliVolts", measuredVoltage);
        map.put("comment", comment);
        hdf5Writer.compound().write(datasetName, map);
    }

    /**
     * Writes a new measurement to <var>datasetName</var> as a list.
     * 
     * @param datasetName The name of the data set to write to.
     * @param measurementDate The date when the measurement was performed.
     * @param measuredTemperature The measured temperature (in degree Celsius).
     * @param measuredVoltage The measured voltage (in milli Volts).
     * @param comment A comment on the measurement.
     */
    void writeMeasurementAsList(String datasetName, Date measurementDate,
            float measuredTemperature, double measuredVoltage, String comment)
    {
        List<Object> list =
                Arrays.<Object> asList(measurementDate, measuredTemperature, measuredVoltage,
                        comment);
        // The compound type name is optional
        HDF5CompoundType<List<?>> type =
                hdf5Writer.compound().getInferredType(
                        "Measurement",
                        Arrays.asList("date", "temperatureInDegreeCelsius", "voltageInMilliVolts",
                                "comment"), list);
        hdf5Writer.compound().write(datasetName, type, list);
    }

    /**
     * Writes a new measurement to <var>datasetName</var> as an array.
     * 
     * @param datasetName The name of the data set to write to.
     * @param measurementDate The date when the measurement was performed.
     * @param measuredTemperature The measured temperature (in degree Celsius).
     * @param measuredVoltage The measured voltage (in milli Volts).
     * @param comment A comment on the measurement.
     */
    void writeMeasurementAsArray(String datasetName, Date measurementDate,
            float measuredTemperature, double measuredVoltage, String comment)
    {
        Object[] array = new Object[]
            { measurementDate, measuredTemperature, measuredVoltage, comment };
        // The compound type name is optional
        HDF5CompoundType<Object[]> type =
                hdf5Writer.compound().getInferredType("Measurement", new String[]
                    { "date", "temperatureInDegreeCelsius", "voltageInMilliVolts", "comment" }, array);
        hdf5Writer.compound().write(datasetName, type, array);
    }

    /**
     * Reads a measurement at <var>datasetName</var>.
     * 
     * @param datasetName The name of the data set to write to.
     */
    Measurement readMeasurement(String datasetName)
    {
        return hdf5Reader.compound().read(datasetName, Measurement.class);
    }

    /**
     * Reads a measurement at <var>datasetName</var> and returns it as a map.
     * 
     * @param datasetName The name of the data set to write to.
     */
    HDF5CompoundDataMap readMeasurementToMap(String datasetName)
    {
        return hdf5Reader.compound().read(datasetName, HDF5CompoundDataMap.class);
    }

    /**
     * Reads a measurement at <var>datasetName</var> and returns it as a list.
     * 
     * @param datasetName The name of the data set to write to.
     */
    HDF5CompoundDataList readMeasurementToList(String datasetName)
    {
        return hdf5Reader.compound().read(datasetName, HDF5CompoundDataList.class);
    }

    /**
     * Reads a measurement at <var>datasetName</var> and returns it as an <code>Object[]</code>.
     * 
     * @param datasetName The name of the data set to write to.
     */
    Object[] readMeasurementToArray(String datasetName)
    {
        return hdf5Reader.compound().read(datasetName, Object[].class);
    }

    public static void main(String[] args)
    {
        // Open "voltageMeasurements.h5" for writing
        FullVoltageMeasurementCompoundExample e =
                new FullVoltageMeasurementCompoundExample("voltageMeasurements.h5", false);
        e.writeMeasurement("/experiment3/measurement1", new Date(), 18.6f, 15.38937516,
                "Temperature measurement seems to be flaky.");
        // See what we've written out
        System.out.println("Compound record: " + e.readMeasurement("/experiment3/measurement1"));

        // Alternative approaches to writing a compound data set
        // Note: all of those use their own compound data type.
        // If you rely on all having the same compound data type, you need to specify 
        e.writeMeasurementAsMap("/experiment3/measurement2", new Date(
                System.currentTimeMillis() - 10000L), 18.5f, 12.74630652, "-");
        e.writeMeasurementAsList("/experiment3/measurement3", new Date(
                System.currentTimeMillis() - 20000L), 18.1f, 11.275649054, "-");
        e.writeMeasurementAsArray("/experiment3/measurement4", new Date(
                System.currentTimeMillis() - 30000L), 17.84f, 9.58736193, "-");
        e.close();

        // Open "voltageMeasurements.h5" for reading
        FullVoltageMeasurementCompoundExample eRO =
                new FullVoltageMeasurementCompoundExample("voltageMeasurements.h5", true);
        // Note that we have specified CompoundElement and set a different member name for the
        // fields "temperature" and "voltage"
        System.out.println("Compound record as map: "
                + eRO.readMeasurementToMap("/experiment3/measurement1"));
        System.out.println("Compound record as list: "
                + eRO.readMeasurementToList("/experiment3/measurement1"));
        System.out.println("Compound record as an array: "
                + ArrayUtils.toString(eRO.readMeasurementToArray("/experiment3/measurement1")));

        // Print the other measurements records, it doesn't matter how they got written
        System.out.println("Second compound record: "
                + eRO.readMeasurement("/experiment3/measurement2"));
        System.out.println("Third compound record: "
                + eRO.readMeasurement("/experiment3/measurement3"));
        System.out.println("Fourth compound record: "
                + eRO.readMeasurement("/experiment3/measurement4"));
        eRO.close();
    }

}
