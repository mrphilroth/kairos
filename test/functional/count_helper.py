from helper_helper import *
from helper_helper import _time

from collections import OrderedDict

@unittest.skipUnless( os.environ.get('TEST_COUNT','true').lower()=='true', 'skipping counts' )
class CountHelper(Chai):

  def setUp(self):
    super(CountHelper,self).setUp()

    self.series = Timeseries(self.client, type='count', prefix='kairos',
      read_func=int,
      intervals={
        'minute' : {
          'step' : 60,
          'steps' : 5,
        },
        'hour' : {
          'step' : 3600,
          'resolution' : 60,
        }
      } )
    self.series.delete_all()

  def tearDown(self):
    self.series.delete_all()

  def test_bulk_insert(self):
    inserts = {
      None      : { 'test1':[1,2,3], 'test2':[4,5,6] },
      _time(0)  : { 'test1':[1,2,3], 'test2':[4,5,6], 'test3':[7,8,9] },
      _time(30) : { 'test1':[1,2,3], 'test2':[4,5,6] },
      _time(60) : { 'test1':[1,2,3], 'test3':[7,8,9] }
    }
    self.series.bulk_insert( inserts )

    t1_i1 = self.series.get('test1', 'minute', timestamp=_time(0))
    assert_equals( 1+2+3+1+2+3, t1_i1[_time(0)] )

    t2_i1 = self.series.get('test2', 'minute', timestamp=_time(0))
    assert_equals( 4+5+6+4+5+6, t2_i1[_time(0)] )
    
    t3_i1 = self.series.get('test3', 'minute', timestamp=_time(0))
    assert_equals( 7+8+9, t3_i1[_time(0)] )

    t1_i2 = self.series.get('test1', 'minute', timestamp=_time(60))
    assert_equals( 1+2+3, t1_i2[_time(60)] )

  def test_bulk_insert_intervals_after(self):
    a,b,c,d,e,f = 10,11,12,13,14,15
    inserts = OrderedDict( (
      (None     , { 'test1':[1,2,3], 'test2':[4,5,6] } ),
      (_time(0) , { 'test1':[1,2,3], 'test2':[4,5,6], 'test3':[7,8,9] } ),
      (_time(30), { 'test1':[1,2,3], 'test2':[4,5,6] } ),
      (_time(60), { 'test1':[a,b,c], 'test3':[d,e,f] })
    ) )
    self.series.bulk_insert( inserts, intervals=3 )

    t1_i1 = self.series.get('test1', 'minute', timestamp=_time(0))
    assert_equals( 1+2+3+1+2+3, t1_i1[_time(0)] )

    t2_i1 = self.series.get('test2', 'minute', timestamp=_time(0))
    assert_equals( 4+5+6+4+5+6, t2_i1[_time(0)] )
    
    t3_i1 = self.series.get('test3', 'minute', timestamp=_time(0))
    assert_equals( 7+8+9, t3_i1[_time(0)] )

    t1_i2 = self.series.get('test1', 'minute', timestamp=_time(60))
    assert_equals( 1+2+3+1+2+3+a+b+c, t1_i2[_time(60)] )

    t3_i3 = self.series.get('test3', 'minute', timestamp=_time(120))
    assert_equals( 7+8+9+d+e+f, t3_i3[_time(120)] )

    t3_i4 = self.series.get('test3', 'minute', timestamp=_time(180))
    assert_equals( 7+8+9+d+e+f, t3_i4[_time(180)] )

  def test_bulk_insert_intervals_before(self):
    a,b,c,d,e,f = 10,11,12,13,14,15
    inserts = OrderedDict( (
      (None     , { 'test1':[1,2,3], 'test2':[4,5,6] } ),
      (_time(0) , { 'test1':[1,2,3], 'test2':[4,5,6], 'test3':[7,8,9] } ),
      (_time(30), { 'test1':[1,2,3], 'test2':[4,5,6] } ),
      (_time(60), { 'test1':[a,b,c], 'test3':[d,e,f] })
    ) )
    self.series.bulk_insert( inserts, intervals=-3 )

    t1_i1 = self.series.get('test1', 'minute', timestamp=_time(0))
    assert_equals( 1+2+3+1+2+3+a+b+c, t1_i1[_time(0)] )

    t2_i1 = self.series.get('test2', 'minute', timestamp=_time(0))
    assert_equals( 4+5+6+4+5+6, t2_i1[_time(0)] )
    
    t3_i1 = self.series.get('test3', 'minute', timestamp=_time(0))
    assert_equals( 7+8+9+d+e+f, t3_i1[_time(0)] )

    t1_i2 = self.series.get('test1', 'minute', timestamp=_time(-60))
    assert_equals( 1+2+3+1+2+3+a+b+c, t1_i2[_time(-60)] )

    t3_i3 = self.series.get('test3', 'minute', timestamp=_time(-120))
    assert_equals( 7+8+9+d+e+f, t3_i3[_time(-120)] )

    t3_i4 = self.series.get('test3', 'minute', timestamp=_time(-180))
    assert_equals( 7+8+9, t3_i4[_time(-180)] )
  
  def test_get(self):
    # 2 hours worth of data
    for t in xrange(1, 7200):
      self.series.insert( 'test', 1, timestamp=_time(t) )

    ###
    ### no resolution, condensed has no impact
    ###
    # middle of an interval
    interval = self.series.get( 'test', 'minute', timestamp=_time(100) )
    assert_equals( map(_time, [60]), interval.keys() )
    assert_equals( 60, interval[_time(60)] )

    # no matching interval, returns no with empty value list
    interval = self.series.get( 'test', 'minute' )
    assert_equals( 1, len(interval) )
    assert_equals( 0, interval.values()[0] )
    
    ###
    ### with resolution, optionally condensed
    ###
    interval = self.series.get( 'test', 'hour', timestamp=_time(100) )
    assert_equals( 60, len(interval) )
    assert_equals( 60, interval[_time(60)] )
    
    interval = self.series.get( 'test', 'hour', timestamp=_time(100), transform='rate' )
    assert_equals( 1.0, interval[_time(60)] )
    
    interval = self.series.get( 'test', 'hour', timestamp=_time(100), condensed=True )
    assert_equals( 1, len(interval) )
    assert_equals( 3599, interval[_time(0)] )
    
    interval = self.series.get( 'test', 'hour', timestamp=_time(4000), condensed=True )
    assert_equals( 1, len(interval) )
    assert_equals( 3600, interval[_time(3600)] )
    
    interval = self.series.get( 'test', 'hour', timestamp=_time(4000), condensed=True, transform='rate' )
    assert_equals( 1, len(interval) )
    assert_equals( 1.0, interval[_time(3600)] )

  def test_get_joined(self):
    # put some data in the first minutes of each hour for test1, and then for
    # a few more minutes in test2
    for t in xrange(1, 120):
      self.series.insert( 'test1', t, timestamp=_time(t) )
      self.series.insert( 'test2', t, timestamp=_time(t) )
    for t in xrange(3600, 3720):
      self.series.insert( 'test1', t, timestamp=_time(t) )
      self.series.insert( 'test2', t, timestamp=_time(t) )
    for t in xrange(120, 240):
      self.series.insert( 'test1', t, timestamp=_time(t) )
    for t in xrange(3721, 3840):
      self.series.insert( 'test1', t, timestamp=_time(t) )

    ###
    ### no resolution, condensed has no impact
    ###
    # interval with 2 series worth of data
    interval = self.series.get( ['test1','test2'], 'minute', timestamp=_time(100) )
    assert_equals( [_time(60)], interval.keys() )
    assert_equals( 2*sum(range(60,120)), interval[_time(60)] )
    
    interval = self.series.get( ['test1','test2'], 'minute', timestamp=_time(100), transform='rate' )
    assert_equals( (2*sum(range(60,120)))/60.0, interval[_time(60)] )

    # interval with 1 series worth of data
    interval = self.series.get( ['test1','test2'], 'minute', timestamp=_time(122) )
    assert_equals( [_time(120)], interval.keys() )
    assert_equals( sum(range(120,180)), interval[_time(120)] )
    interval = self.series.get( ['test1','test2'], 'minute', timestamp=_time(122), transform='rate' )
    assert_equals( (sum(range(120,180)))/60.0, interval[_time(120)] )

    # no matching interval, returns no with empty value list
    interval = self.series.get( ['test1','test2'], 'minute' )
    assert_equals( 1, len(interval) )
    assert_equals( 0, interval.values()[0] )
    interval = self.series.get( ['test1','test2'], 'minute', transform='rate' )

    ###
    ### with resolution, optionally condensed
    ###
    interval = self.series.get( ['test1','test2'], 'hour', timestamp=_time(100) )
    assert_equals( map(_time,[0,60,120,180]), interval.keys() )
    assert_equals( 2*sum(range(1,60)), interval[_time(0)] )
    assert_equals( 2*sum(range(60,120)), interval[_time(60)] )
    assert_equals( sum(range(120,180)), interval[_time(120)] )
    assert_equals( sum(range(180,240)), interval[_time(180)] )

    interval = self.series.get( ['test1','test2'], 'hour', timestamp=_time(100), condensed=True )
    assert_equals( [_time(0)], interval.keys() )
    assert_equals( 2*sum(range(1,120)) + sum(range(120,240)), interval[_time(0)] )
    
    interval = self.series.get( ['test1','test2'], 'hour', timestamp=_time(100), condensed=True, transform='rate' )
    assert_equals( (2*sum(range(1,120)) + sum(range(120,240)))/3600.0, interval[_time(0)] )

  def test_series(self):
    # 2 hours worth of data
    for t in xrange(1, 7200):
      self.series.insert( 'test', 1, timestamp=_time(t) )

    ###
    ### no resolution, condensed has no impact
    ###
    interval = self.series.series( 'test', 'minute', end=_time(250) )
    assert_equals( map(_time, [0,60,120,180,240]), interval.keys() )
    assert_equals( 59, interval[_time(0)] )
    assert_equals( 60, interval[_time(60)] )
    
    interval = self.series.series( 'test', 'minute', steps=2, end=_time(250) )
    assert_equals( map(_time, [180,240]), interval.keys() )
    assert_equals( 60, interval[_time(240)] )
    
    interval = self.series.series( 'test', 'minute', steps=2, end=_time(250), transform='rate' )
    assert_equals( 1.0, interval[_time(240)] )

    # with collapse
    interval = self.series.series( 'test', 'minute', end=_time(250), collapse=True )
    assert_equals( map(_time, [0]), interval.keys() )
    assert_equals( 299, interval[_time(0)] )
    
    ###
    ### with resolution
    ###
    interval = self.series.series( 'test', 'hour', end=_time(250) )
    assert_equals( 1, len(interval) )
    assert_equals( 60, len(interval[_time(0)]) )
    assert_equals( 59, interval[_time(0)][_time(0)] )
    assert_equals( 60, interval[_time(0)][_time(60)] )

    # single step, last one    
    interval = self.series.series( 'test', 'hour', condensed=True, end=_time(4200) )
    assert_equals( 1, len(interval) )
    assert_equals( 3600, interval[_time(3600)] )
    interval = self.series.series( 'test', 'hour', condensed=True, end=_time(4200), transform='rate' )
    assert_equals( 1.0, interval[_time(3600)] )

    interval = self.series.series( 'test', 'hour', condensed=True, end=_time(4200), steps=2 )
    assert_equals( map(_time, [0,3600]), interval.keys() )
    assert_equals( 3599, interval[_time(0)] )
    assert_equals( 3600, interval[_time(3600)] )

    # with collapse
    interval = self.series.series( 'test', 'hour', condensed=True, end=_time(4200), steps=2, collapse=True )
    assert_equals( map(_time, [0]), interval.keys() )
    assert_equals( 7199, interval[_time(0)] )

  def test_series_joined(self):
    # put some data in the first minutes of each hour for test1, and then for
    # a few more minutes in test2
    for t in xrange(1, 120):
      self.series.insert( 'test1', t, timestamp=_time(t) )
      self.series.insert( 'test2', t, timestamp=_time(t) )
    for t in xrange(3600, 3720):
      self.series.insert( 'test1', t, timestamp=_time(t) )
      self.series.insert( 'test2', t, timestamp=_time(t) )
    for t in xrange(120, 240):
      self.series.insert( 'test1', t, timestamp=_time(t) )
    for t in xrange(3720, 3840):
      self.series.insert( 'test1', t, timestamp=_time(t) )

    ###
    ### no resolution, condensed has no impact
    ###
    interval = self.series.series( ['test1','test2'], 'minute', end=_time(250) )
    assert_equals( map(_time,[0,60,120,180,240]), interval.keys() )
    assert_equals( 2*sum(range(1,60)), interval[_time(0)] )
    assert_equals( 2*sum(range(60,120)), interval[_time(60)] )
    assert_equals( sum(range(120,180)), interval[_time(120)] )
    assert_equals( sum(range(180,240)), interval[_time(180)] )
    assert_equals( 0, interval[_time(240)] )
    interval = self.series.series( ['test1','test2'], 'minute', end=_time(250), transform='rate' )
    assert_equals( sum(range(120,180))/60.0, interval[_time(120)] )

    # no matching interval, returns no with empty value list
    interval = self.series.series( ['test1','test2'], 'minute', start=time.time(), steps=2 )
    assert_equals( 2, len(interval) )
    assert_equals( 0, interval.values()[0] )

    # with collapsed
    interval = self.series.series( ['test1','test2'], 'minute', end=_time(250), collapse=True )
    assert_equals( [_time(0)], interval.keys() )
    assert_equals( 2*sum(range(1,120))+sum(range(120,240)), interval[_time(0)] )

    ###
    ### with resolution, optionally condensed
    ###
    interval = self.series.series( ['test1','test2'], 'hour', end=_time(250) )
    assert_equals( 1, len(interval) )
    assert_equals( map(_time,[0,60,120,180]), interval[_time(0)].keys() )
    assert_equals( 4, len(interval[_time(0)]) )
    assert_equals( 2*sum(range(1,60)), interval[_time(0)][_time(0)] )
    assert_equals( 2*sum(range(60,120)), interval[_time(0)][_time(60)] )
    assert_equals( sum(range(120,180)), interval[_time(0)][_time(120)] )
    assert_equals( sum(range(180,240)), interval[_time(0)][_time(180)] )
    
    interval = self.series.series( ['test1','test2'], 'hour', end=_time(250), transform='rate' )
    assert_equals( sum(range(180,240)) / 60.0, interval[_time(0)][_time(180)] )

    # condensed
    interval = self.series.series( ['test1','test2'], 'hour', end=_time(250), condensed=True )
    assert_equals( [_time(0)], interval.keys() )
    assert_equals( 2*sum(range(1,120))+sum(range(120,240)), interval[_time(0)] )

    # with collapsed
    interval = self.series.series( ['test1','test2'], 'hour', condensed=True, end=_time(4200), steps=2, collapse=True )
    assert_equals( map(_time, [0]), interval.keys() )
    assert_equals(
      2*sum(range(1,120))+sum(range(120,240))+2*sum(range(3600,3720))+sum(range(3720,3840)),
      interval[_time(0)] )
