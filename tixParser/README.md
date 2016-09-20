<h1 align="center"> lvm4j </h1>

[![Build Status](https://travis-ci.org/dirmeier/lvm4j.svg?branch=master)](https://travis-ci.org/dirmeier/lvm4j.svg?branch=master)
[![codecov](https://codecov.io/gh/dirmeier/lvm4j/branch/master/graph/badge.svg)](https://codecov.io/gh/dirmeier/lvm4j)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/28c9723c26b04237b94895f035dc5b32)](https://www.codacy.com/app/simon-dirmeier/lvm4j?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dirmeier/lvm4j&amp;utm_campaign=Badge_Grade)

Latent variable models in Java.

## Introduction

Latent variable models are well-established statistical models where some of the data are not observed. I demonstrate implementations of some of these models in Java. For the sake of simplicity I refer to every model as latent if it consists of two disjoint sets of variables, one that is observed and one that is hidden (e.g. we don't have data or they are just not observable at all). 

The most famous and magnificient of them all, the <i>Hidden Markov Model</i>, is applicable to a diverse number of fields (e.g. for secondary structure prediction or alignment of viral RNA to a reference genome). With new versions I will try to cover more latent variable models in <code>lvm4j</code>. For now only HMMs are implemented and an example of how they are used are included.

## Installation
 
You can either install the package by hand if you do not want to use maven (why would you?) or just use the standard waytogo installation using a maven project (and pom.xml).

### Install package without maven

1) Call

```sh
./make.sh
```

from the source folder.

2) Include <code>lvm4j.jar</code> as external library in your Java project.

### Install package with maven

1) Include my maven repository in your 'pom.xml':

```xml
<repositories>
	<repository>
    	<id>central</id>
    	<url>http://digital-alexandria.net:8081/artifactory/libs-release</url>
    	<snapshots>
    	    <enabled>false</enabled>
    	</snapshots>
	</repository>
</repositories>
```

2) Include the dependency in your 'pom.xml':

```xml
<dependency>
    <groupId>net.digital_alexandria</groupId>
    <artifactId>commandline-parser</artifactId>
    <version>1.1.2</version>
</dependency>
```

3) That's it.

## Usage

Here, we briefly describe how the <code>lvm4j</code> libary is used. So far the following latent variable models are implemented.

* HMM (a discrete-state-discrete-observation latent variable model)

### How to use the HMM

[![Link to HMM](/logos/hmm.pdf)](/logos/hmm.pdf)


Using an HMM (in v0.1) involves two steps: training of emission and transition probabilities and prediction of the latent state sequence.

#### Training

First initialize an HMM using:

```java
char[] states = new char[]{'A', 'B', 'C'};
char[] observations = new char[]{'X', 'Y', 'Z'};
HMM hmm = HMMFactory.instance().hmm(states, observations, 1);
```

It is easier though to take the constructor that takes a single string only that contains the path to an XML-file.

```java
String xmlFile = "/src/test/resources/hmm.xml";
HMM hmm = HMMFactory.instance().hmm(xmlFile);
```

Having the HMM initialized, training is done like this:

```java
Map<String, String> states = new HashMap<>(){{
	put("s1", "ABCABC");
	put("s2", "ABCCCC");
}};
Map<String, String> observations = new HashMap<>(){{
	put("s1", "XYZYXZ");
	put("s2", "XYZYXZ");
}};
hmm.train(states, observations);
```

Take care that <code>states</code> and <code>observations</code> have the same keys and equally long values. You can write your trained HMM to a file using:

```java
String outFile = "hmm.trained.xml";
hmm.writeHMM(outFile);
```

That is it! 

#### Prediction

First initialize the HMM again:

```java
String xmlFile = "/src/test/resources/hmm.trained.xml";
HMM hmm = HMMFactory.instance().hmm(xmlFile)
```

Make sure to use the <code>hmm.trained.xml</code> file containing your trained HMM. Then make a prediction using:

```java
Map<String, String> observations = new HashMap<>(){{
	put("s1", "XYZYXZ");
	put("s2", "XYZYXZ");
}};
Map<String, String> pred = hmm.predict(states, observations);
```

Congrats! That concludes the tutorial on HMMs. 

## Author

* Simon Dirmeier <a href="mailto:simon.dirmeier@gmx.de">simon.dirmeier@gmx.de</a>
